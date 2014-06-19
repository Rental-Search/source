# -*- coding: utf-8 -*-
import datetime
import urllib
import uuid
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

from payments.models import PayboxDirectPaymentInformation, PayboxDirectPlusPaymentInformation, NonPaymentInformation
from payments.paybox_payment import PayboxManager, PayboxException
from payments.abstract_payment import PaymentException
from accounts.forms import EmailAuthenticationForm, BookingCreditCardForm, ExistingBookingCreditCardForm
from accounts.models import Patron, CreditCard
from products.forms import FacetedSearchForm
from products.models import Product
from products.choices import PAYMENT_TYPE
from rent.models import Booking, ProBooking, BorrowerComment
from rent.forms import BookingForm, BookingConfirmationForm

from eloue.geocoder import GoogleGeocoder
from eloue.wizard import MultiPartFormWizard

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

from django import forms
class A(forms.Form):
    pass

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
        
        from products.search import product_search
        self.extra_context={
            'product_list': product_search.more_like_this(product)[:4]
        }
        if request.method == "POST":
            if product.payment_type != PAYMENT_TYPE.NOPAY and not product.owner.current_subscription:
                if request.user.is_authenticated():
                    try:
                        request.user.creditcard
                        self.form_list.append(ExistingBookingCreditCardForm)
                    except CreditCard.DoesNotExist:
                        self.form_list.append(BookingCreditCardForm)
                elif EmailAuthenticationForm in self.form_list:
                     form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                     if form.is_valid():
                        user = form.get_user()
                        try:
                            user.creditcard
                            self.form_list.append(ExistingBookingCreditCardForm)
                        except (CreditCard.DoesNotExist, AttributeError):
                            self.form_list.append(BookingCreditCardForm)
            else:
                self.form_list.append(A)

        return super(BookingWizard, self).__call__(request, product, *args, **kwargs)

    def done(self, request, form_list):
        super(BookingWizard, self).done(request, form_list)
        booking_form = form_list[0]
        
        creditcard_form = next(
            itertools.ifilter(
                lambda form: isinstance(form, (BookingCreditCardForm, ExistingBookingCreditCardForm)), 
                form_list
            ),
            None
        )
        from django.forms.models import model_to_dict
        if self.new_patron == booking_form.instance.product.owner:
            messages.error(request, _(u"Vous ne pouvez pas louer vos propres objets"))
            return redirect(booking_form.instance.product)
        
        booking = booking_form.save(commit=False)
        booking.ip = request.META.get('REMOTE_ADDR', None)
        unit = Booking.calculate_price(booking.product,
            booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])
        max_available = Booking.calculate_available_quantity(booking.product, booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])
        
        booking.total_amount = unit[1] * (1 if booking_form.cleaned_data['quantity'] is None else (booking_form.cleaned_data['quantity'] if max_available >= booking_form.cleaned_data['quantity'] else max_available))

        booking.borrower = self.new_patron

        if creditcard_form:
            cleaned_data = creditcard_form.cleaned_data
            if creditcard_form.instance.pk is None:
                if cleaned_data.get('keep'):
                    creditcard_form.instance.holder = self.new_patron
                creditcard_form.instance.subscriber_reference = uuid.uuid4().hex
            if any(cleaned_data.values()):
                creditcard = creditcard_form.save()
            else:
                creditcard = request.user.creditcard
            payment = PayboxDirectPlusPaymentInformation.objects.create(creditcard=creditcard)
            preapproval_parameters = {'cvv': cleaned_data.get('cvv', '')}
        else:
            preapproval_parameters = {}
            payment = NonPaymentInformation.objects.create()

        booking.payment = payment
        booking.save()

        try:
            booking.preapproval(**preapproval_parameters)
        except PaymentException as e:
            booking.state = Booking.STATE.REJECTED
            booking.save()
            return redirect('booking_failure', booking.pk.hex)
        else:
            GoalRecord.record('rent_object_pre_paypal', WebUser(request))
            return redirect('booking_success', booking.pk.hex)

    
    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if issubclass(next_form, BookingForm):
            product = self.extra_context['product']
            if product.owner.current_subscription:
                booking = ProBooking(product=product, owner=product.owner, state=Booking.STATE.PROFESSIONAL)
            else:
                booking = Booking(product=product, owner=product.owner)
            started_at = datetime.datetime.now() + datetime.timedelta(days=1)
            ended_at = started_at + datetime.timedelta(days=1)
            initial = {
                'started_at': [started_at.strftime('%d/%m/%Y'), started_at.strftime("08:00:00")],
                'ended_at': [ended_at.strftime('%d/%m/%Y'), ended_at.strftime("08:00:00")],
            }
            initial.update(self.initial.get(step, {}))
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial, instance=booking)
        elif issubclass(next_form, (BookingCreditCardForm, ExistingBookingCreditCardForm)):
            user = self.user if self.user.is_authenticated() else self.new_patron
            try:
                # in the ModelForm._post_clean hook the instance is updated with the values of cleaned_data,
                # and _post_clean is called always, even when the form is invalid
                # so we have to pass a copy, because we don't want to get request.user.creditcard modified
                from copy import copy
                instance = copy(user.creditcard)
            except (CreditCard.DoesNotExist, AttributeError):
                instance = CreditCard()
            return next_form(
                data, files, prefix=self.prefix_for_step(step), 
                instance=instance, initial={'holder_name': '', 'expires': ''}
            )
        return super(BookingWizard, self).get_form(step, data, files)
    
    def process_step(self, request, form, step):
        super(BookingWizard, self).process_step(request, form, step)
        self.extra_context.setdefault('preview', {}).update(form.cleaned_data)
    
    def parse_params(self, request, product, number, *args, **kwargs):
        self.extra_context['product'] = product
        self.extra_context['prices'] = product.prices.filter(unit=1)
        self.extra_context['number'] = number
        self.extra_context['comments'] = BorrowerComment.objects.filter(booking__product=product)
        self.extra_context['insurance_available'] = settings.INSURANCE_AVAILABLE
        if product.is_archived:
            location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
            address = location.get('formatted_address') or (u'{city}, {country}'.format(**location) if location.get('city') else u'{country}'.format(**location))
            self.extra_context['search_form'] = FacetedSearchForm({'l': address}, auto_id='id_for_%s')

    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'products/product_detail.html'
        elif issubclass(self.form_list[step], (BookingCreditCardForm, ExistingBookingCreditCardForm, A)):
            return 'rent/booking_confirm.html'
        else:
            return 'accounts/auth_missing.html'


class PhoneBookingWizard(BookingWizard):

    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'products/phone_view.html'
        elif issubclass(self.form_list[step], (BookingCreditCardForm, ExistingBookingCreditCardForm, A)):
            return 'rent/booking_confirm.html'
        else:
            return 'accounts/auth_missing.html'
