# -*- coding: utf-8 -*-
import datetime
import urllib
import itertools
from decimal import Decimal as D

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template, redirect_to

from eloue.payments.models import PayboxDirectPaymentInformation, PayboxDirectPlusPaymentInformation, NonPaymentInformation
from eloue.payments.paybox_payment import PayboxManager, PayboxException
from eloue.payments.abstract_payment import PaymentException
from eloue.accounts.forms import EmailAuthenticationForm, BookingCreditCardForm, CvvForm
from eloue.accounts.models import Patron, Avatar, CreditCard
from eloue.geocoder import GoogleGeocoder
from eloue.products.forms import FacetedSearchForm
from eloue.products.models import Product, PAYMENT_TYPE
from eloue.rent.models import Booking, BorrowerComment
from eloue.rent.forms import BookingForm, BookingConfirmationForm
from eloue.wizard import MultiPartFormWizard

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


class BookingWizard(MultiPartFormWizard):
    
    def __init__(self, *args, **kwargs):
        super(BookingWizard, self).__init__(*args, **kwargs)
        self.required_fields = [
          'username', 'password1', 'password2', 'is_professional', 'company_name', 'first_name', 'last_name',
          'phones', 'phones__phone', 'addresses',
          'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country',
        ]
        self.title = _(u'Réservation')

    def __call__(self, request, product, *args, **kwargs):
        if product.name == 'carproduct':
            self.required_fields += ['drivers_license_date', 'drivers_license_number', 'date_of_birth', 'place_of_birth']
        
        from eloue.products.search_indexes import product_search
        self.extra_context={
            'product_list': product_search.more_like_this(product)[:4]
        }
        if request.method == "POST":
            if product.payment_type != PAYMENT_TYPE.NOPAY:
                if request.user.is_authenticated():
                    try:
                        request.user.creditcard
                        self.form_list.append(CvvForm)
                    except (CreditCard.DoesNotExist):
                        self.form_list.append(BookingCreditCardForm)
                elif EmailAuthenticationForm in self.form_list:
                     form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                     if form.is_valid():
                        user = form.get_user()
                        try:
                            user.creditcard
                            self.form_list.append(CvvForm)
                        except (CreditCard.DoesNotExist, AttributeError):
                            self.form_list.append(BookingCreditCardForm)
        return super(BookingWizard, self).__call__(request, product, *args, **kwargs)

    def done(self, request, form_list):
        super(BookingWizard, self).done(request, form_list)
        booking_form = form_list[0]
        
        creditcard_form = next(
            itertools.ifilter(
                lambda form: isinstance(form, (BookingCreditCardForm, CvvForm)), 
                form_list
            ),
            None
        )

        if self.new_patron == booking_form.instance.product.owner:
            messages.error(request, _(u"Vous ne pouvez pas louer vos propres objets"))
            return redirect_to(request, booking_form.instance.product.get_absolute_url())
        
        booking = booking_form.save(commit=False)
        booking.ip = request.META.get('REMOTE_ADDR', None)
        booking.total_amount = Booking.calculate_price(booking.product,
            booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])[1]
        booking.borrower = self.new_patron

        if creditcard_form:
            if creditcard_form.instance.pk is None:
                creditcard_form.instance.holder = self.new_patron
            creditcard = creditcard_form.save()
            preapproval_parameters = (creditcard, creditcard_form.cleaned_data['cvv'])
            payment = PayboxDirectPlusPaymentInformation(booking=booking)
        else:
            preapproval_parameters = ()
            payment = NonPaymentInformation()

        payment.save()
        booking.payment = payment
        booking.save()

        try:
            booking.preapproval(*preapproval_parameters)
        except PaymentException as e:
            booking.state = Booking.STATE.REJECTED
            booking.save()

        if booking.state == Booking.STATE.AUTHORIZED:
            GoalRecord.record('rent_object_pre_paypal', WebUser(request))
            return redirect('booking_success', booking.pk.hex)
        return redirect('booking_failure', booking.pk.hex)

    
    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if issubclass(next_form, BookingForm):
            product = self.extra_context['product']
            booking = Booking(product=product, owner=product.owner)
            started_at = datetime.datetime.now() + datetime.timedelta(days=1)
            ended_at = started_at + datetime.timedelta(days=1)
            initial = {
                'started_at': [started_at.strftime('%d/%m/%Y'), started_at.strftime("08:00:00")],
                'ended_at': [ended_at.strftime('%d/%m/%Y'), ended_at.strftime("08:00:00")],
                # is 'total_amount' really necessary?
                # 'total_amount': Booking.calculate_price(product, started_at, ended_at)[1]
                # it is not
            }
            initial.update(self.initial.get(step, {}))
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial, instance=booking)
        elif issubclass(next_form, (BookingCreditCardForm, CvvForm)):
            from eloue.accounts.models import CreditCard
            user = self.user if self.user.is_authenticated() else self.new_patron
            try:
                instance = user.creditcard
            except (CreditCard.DoesNotExist, AttributeError):
                if user:
                    instance = CreditCard(holder=user)
                else:
                    instance = CreditCard()
            return next_form(
                data, files, prefix=self.prefix_for_step(step), 
                instance=instance
            )
        return super(BookingWizard, self).get_form(step, data, files)
    
    def process_step(self, request, form, step):
        super(BookingWizard, self).process_step(request, form, step)
        self.extra_context.setdefault('preview', {}).update(form.cleaned_data)
    
    def parse_params(self, request, product, *args, **kwargs):
        self.extra_context['product'] = product
        self.extra_context['prices'] = product.prices.filter(unit=1)
        self.extra_context['search_form'] = FacetedSearchForm()
        self.extra_context['comments'] = BorrowerComment.objects.filter(booking__product=product)
        self.extra_context['insurance_available'] = settings.INSURANCE_AVAILABLE
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'products/product_detail.html'
        elif issubclass(self.form_list[step], (BookingCreditCardForm, CvvForm)):
            return 'rent/booking_confirm.html'
        else:
            return 'accounts/auth_missing.html'
    
