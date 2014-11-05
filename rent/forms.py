# -*- coding: utf-8 -*-
import datetime
from django.utils import formats
import logbook

from dateutil import parser

from django import forms
from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from accounts.forms import CreditCardForm

from rent.models import Booking, Sinister, OwnerComment, BorrowerComment
from rent.utils import DATE_FORMAT, DATE_TIME_FORMAT
from rent.choices import TIME_CHOICE

from eloue import legacy

log = logbook.Logger('eloue.rent')

BOOKING_DAYS = getattr(settings, 'BOOKING_DAYS', 85)


class ISO8601DateTimeField(forms.Field):
    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        return parser.parse(value)
    

class DateTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None, *args, **kwargs):
        widgets = (
            forms.DateInput(attrs={'class': 'ins dps date-input'}, format=date_format),
            forms.Select(choices=TIME_CHOICE, attrs={'class': 'sells'}),
        )
        super(DateTimeWidget, self).__init__(widgets, *args, **kwargs)
    
    def decompress(self, value):
        if value:
            return [value.date(), value.strftime("%H:%M:%S")]
        return [None, None]
    

class HiddenDateTimeWidget(DateTimeWidget):
    is_hidden = True
    
    def __init__(self, *args, **kwargs):
        super(HiddenDateTimeWidget, self).__init__(*args, **kwargs)
        self.widgets = map(lambda widget: forms.HiddenInput(), self.widgets)
    

class DateTimeField(forms.MultiValueField):
    widget = DateTimeWidget
    hidden_widget = HiddenDateTimeWidget
    default_error_messages = {
        'invalid_date': _(u'Enter a valid date.'),
        'invalid_time': _(u'Enter a valid time.'),
    }
    
    def __init__(self, input_date_formats=None, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        localize = kwargs.get('localize', False)
        fields = (
            forms.DateField(input_formats=input_date_formats,
                      error_messages={'invalid': errors['invalid_date']},
                      localize=localize),
            forms.ChoiceField(choices=TIME_CHOICE)
        )
        super(DateTimeField, self).__init__(fields, *args, **kwargs)
    
    def compress(self, data_list):
        if data_list:
            if data_list[0] in validators.EMPTY_VALUES:
                raise forms.ValidationError(_(u'Enter a valid date.'))
            if data_list[1] in validators.EMPTY_VALUES:
                raise forms.ValidationError(_(u'Enter a valid time.'))
            time = datetime.time(*[int(part) for part in data_list[1].split(':')])
            return datetime.datetime.combine(data_list[0], time)
        return None
    

class PreApprovalIPNForm(forms.Form):
    approved = legacy.TypedChoiceField(required=True, coerce=lambda x: x == 'true', choices=(('true', 'True'), ('false', 'False')))
    preapproval_key = forms.CharField(required=True)
    currency_code = forms.CharField()
    starting_date = ISO8601DateTimeField(required=True)
    ending_date = ISO8601DateTimeField(required=True)
    max_total_amount_of_all_payments = forms.DecimalField(max_digits=8, decimal_places=2, required=True)
    sender_email = forms.CharField(required=True)
    status = forms.CharField(required=True)
    
    def clean_preapproval_key(self):
        preapproval_key = self.cleaned_data['preapproval_key']
        if not Booking.objects.filter(preapproval_key=preapproval_key).exists():
            raise ValidationError(_(u"Cette transaction ne semble pas lier à une transaction interne"))
        return preapproval_key
    

class PayIPNForm(forms.Form):
    action_type = forms.CharField(required=True)
    fees_payer = forms.CharField(required=True)
    pay_key = forms.CharField(required=True)
    sender_email = forms.CharField(required=True)
    status = forms.CharField(required=True)
    
    def clean_pay_key(self):
        pay_key = self.cleaned_data['pay_key']
        if not Booking.objects.filter(pay_key=pay_key).exists():
            raise ValidationError(_(u"Cette transaction ne semble pas lier à une transaction interne"))
        return pay_key
    

class BookingForm(forms.ModelForm):
    started_at = DateTimeField(required=True, input_date_formats=DATE_FORMAT)
    ended_at = DateTimeField(required=True, input_date_formats=DATE_FORMAT)
    quantity = forms.IntegerField(required=False, widget=forms.HiddenInput(), initial=1)

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        if self.instance.product.quantity > 1:
            widget = forms.Select(choices=enumerate(xrange(1, 1 + self.instance.product.quantity), start=1))
            self.fields['quantity'].widget = widget
    
    class Meta:
        model = Booking
        fields = ('started_at', 'ended_at', 'quantity')
    
    def clean(self):
        super(BookingForm, self).clean()
        started_at = self.cleaned_data.get('started_at')
        ended_at = self.cleaned_data.get('ended_at')
        quantity = self.cleaned_data.get('quantity')

        product = self.instance.product

        if (started_at and ended_at):
            self.max_available = Booking.calculate_available_quantity(product, started_at, ended_at)

            if not self.max_available:
                    raise ValidationError(u"Il n'y a aucun produit disponible pendant la période choisie")
            
            if started_at <= datetime.datetime.now() or ended_at <= datetime.datetime.now():
                raise ValidationError(_(u"Vous ne pouvez pas louer à ces dates"))
            if started_at >= ended_at:
                raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))
            if (ended_at - started_at) > datetime.timedelta(days=BOOKING_DAYS):
                raise ValidationError(_(u"La durée d'une location est limitée à %s jours."%BOOKING_DAYS))
            
            unit = product.calculate_price(started_at, ended_at)
            
            if not unit[1]:
                raise ValidationError(_(u"Prix sur devis"))

            self.cleaned_data['price_unit'] = unit[0]
            
            self.cleaned_data['total_amount'] = unit[1] * (1 if quantity is None else (quantity if self.max_available >= quantity else self.max_available))
        
        return self.cleaned_data


class BookingCreditCardForm(CreditCardForm):
    class Meta(CreditCardForm.Meta):
        # see note: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#using-a-subset-of-fields-on-the-form
        # we excluded, then added, to avoid save automatically the card_number
        exclude = ('card_number', 'holder', 'masked_number')


class ExistingBookingCreditCardForm(CreditCardForm):
    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)
        self.fields['cvv'].required=False
        self.fields['expires'].required=False
        self.fields['holder_name'].required=False
        self.fields['card_number'].required=False

    def clean(self):
        if self.errors:
            return self.cleaned_data
        if not self.instance or self.instance.pk is None:
            raise forms.ValidationError(_('You have to bind an existing instance to this form'))
        cvv = self.cleaned_data.get('cvv')
        holder_name = self.cleaned_data.get('holder_name')
        card_number = self.cleaned_data.get('card_number')
        expires = self.cleaned_data.get('expires')
        if any((cvv, holder_name, card_number, expires)):
            if not all((cvv, holder_name, card_number, expires)):
                raise forms.ValidationError(_('You have to fill out all the fields'))
            return super(ExistingBookingCreditCardForm, self).clean()
        return self.cleaned_data

    def save(self, *args, **kwargs):
        cvv = self.cleaned_data.get('cvv')
        holder_name = self.cleaned_data.get('holder_name')
        card_number = self.cleaned_data.get('card_number')
        expires = self.cleaned_data.get('expires')
        if any((cvv, holder_name, card_number, expires)):
            return super(ExistingBookingCreditCardForm, self).save(*args, **kwargs)
        return self.instance


class BookingOfferForm(forms.ModelForm):
    started_at = DateTimeField(required=True, input_date_formats=DATE_FORMAT)
    ended_at = DateTimeField(required=True, input_date_formats=DATE_FORMAT)
    quantity = forms.IntegerField(widget=forms.Select(choices=enumerate(xrange(5))))
    total_amount = forms.DecimalField()

    class Meta:
        model = Booking
        fields = ('started_at', 'ended_at', 'quantity', 'total_amount')

class BookingConfirmationForm(forms.Form):
    pass


class BookingAcceptForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ()
    
    def clean(self):
        started_at = self.instance.started_at
        ended_at = self.instance.ended_at
        quantity = self.instance.quantity
        product = self.instance.product
        
        max_available = Booking.calculate_available_quantity(product, started_at, ended_at)
        if (quantity > max_available):
            raise ValidationError(_(u'Quantité disponible à cette période: %s') % max_available)
        if (started_at and ended_at):
            if started_at <= datetime.datetime.now() or ended_at <= datetime.datetime.now():
                raise ValidationError(_(u"Vous ne pouvez pas louer à ces dates"))
        return self.cleaned_data


class SinisterForm(forms.ModelForm):
    class Meta:
        model = Sinister
        fields = ('description',)


class OwnerCommentForm(forms.ModelForm):
    class Meta:
        model = OwnerComment
        fields = ('note', 'comment', )

class BorrowerCommentForm(forms.ModelForm):
    class Meta:
        model = BorrowerComment
        fields = ('note', 'comment', )


# API 2.0

class Api20BookingForm(BookingForm):
    started_at = forms.DateTimeField(required=True, input_formats=DATE_TIME_FORMAT)
    ended_at = forms.DateTimeField(required=True, input_formats=DATE_TIME_FORMAT)

    def clean(self):
        # TODO: Validation for api is slightly different than validation for form.
        # TODO: Api action should be rewritten to not use form at all.
        super(BookingForm, self).clean()
        started_at = self.cleaned_data.get('started_at')
        ended_at = self.cleaned_data.get('ended_at')
        quantity = self.cleaned_data.get('quantity')

        product = self.instance.product

        if started_at and ended_at:
            self.max_available = Booking.calculate_available_quantity(product, started_at, ended_at)

            if started_at <= datetime.datetime.now() or ended_at <= datetime.datetime.now():
                self.max_available = 0
            if started_at >= ended_at:
                raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))
            if (ended_at - started_at) > datetime.timedelta(days=BOOKING_DAYS):
                raise ValidationError(_(u"La durée d'une location est limitée à %s jours."%BOOKING_DAYS))

            unit = product.calculate_price(started_at, ended_at)

            if not unit[1]:
                raise ValidationError(_(u"Prix sur devis"))

            self.cleaned_data['price_unit'] = unit[0]

            self.cleaned_data['total_amount'] = unit[1] * (1 if quantity is None else (quantity if self.max_available >= quantity else self.max_available))

        return self.cleaned_data
