# -*- coding: utf-8 -*-
import datetime
import urllib
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
          'username', 'password1', 'password2', 'is_professional', 'company_name', 'first_name', 'last_name', 'avatar',
          'phones', 'phones__phone', 'addresses',
          'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country'
        ]

    def __call__(self, request, *args, **kwargs):
        product = get_object_or_404(Product.on_site.select_related(), pk=kwargs['product_id'])
        from eloue.products.search_indexes import product_search
        self.extra_context={
            'product_list': product_search.more_like_this(product)[:4]
        }
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
        return super(BookingWizard, self).__call__(request, *args, **kwargs)

    def done(self, request, form_list):
        super(BookingWizard, self).done(request, form_list)
        booking_form = form_list[0]
        import itertools
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
        
        from eloue.payments.models import PayboxDirectPaymentInformation, PayboxDirectPlusPaymentInformation, NonPaymentInformation
        from eloue.payments.paybox_payment import PayboxManager, PayboxException
        booking = booking_form.save(commit=False)
        booking.ip = request.META.get('REMOTE_ADDR', None)
        booking.total_amount = Booking.calculate_price(booking.product,
            booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])[1]
        booking.borrower = self.new_patron
        if creditcard_form:
            if creditcard_form.cleaned_data.get('save'):
                creditcard_form.instance.holder = self.new_patron
                creditcard = creditcard_form.save(commit=bool(creditcard_form.cleaned_data.get('save')))
            else:
                creditcard = creditcard_form.save(commit=False)
            try:
                request.user.creditcard
                payment = PayboxDirectPlusPaymentInformation(booking=booking)
            except CreditCard.DoesNotExist:
                payment = PayboxDirectPaymentInformation(booking=booking)
            preapproval_parameters = (creditcard, creditcard_form.cleaned_data['cvv'])
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
                'total_amount': Booking.calculate_price(product, started_at, ended_at)[1]
            }
            initial.update(self.initial.get(step, {}))
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial, instance=booking)
        elif issubclass(next_form, (BookingCreditCardForm, CvvForm)):
            from eloue.accounts.models import CreditCard

            try:
                instance = self.new_patron.creditcard
            except (CreditCard.DoesNotExist, AttributeError):
                if self.new_patron:
                    instance = CreditCard(holder=self.new_patron)
                else:
                    instance = CreditCard()
            return next_form(
                data, files, prefix=self.prefix_for_step(step), 
                instance=instance
            )
        return super(BookingWizard, self).get_form(step, data, files)
    
    def process_step(self, request, form, step):
        super(BookingWizard, self).process_step(request, form, step)
        form = self.get_form(0, request.POST, request.FILES)
        if form.is_valid():
            self.extra_context['preview'] = form.cleaned_data
    
    def parse_params(self, request, *args, **kwargs):
        product = get_object_or_404(Product.on_site.active().select_related(), pk=kwargs['product_id'])
        self.extra_context['product'] = product
        self.extra_context['search_form'] = FacetedSearchForm()
        self.extra_context['comments'] = BorrowerComment.objects.filter(booking__product=product)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'products/product_detail.html'
        elif issubclass(self.form_list[step], BookingConfirmationForm):
            return 'rent/booking_confirm.html'
        elif issubclass(self.form_list[step], (BookingCreditCardForm, CvvForm)):
            return 'accounts/credit_card.html'
        else:
            return 'accounts/auth_missing.html'
    
