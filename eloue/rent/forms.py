# -*- coding: utf-8 -*-
import datetime
import logbook

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.rent.models import Booking, Sinister

log = logbook.Logger('eloue.rent')

TIME_CHOICE = (
    ('00:00:00', '00h'),
    ('01:00:00', '01h'),
    ('02:00:00', '02h'),
    ('03:00:00', '03h'),
    ('04:00:00', '04h'),
    ('05:00:00', '05h'),
    ('06:00:00', '06h'),
    ('07:00:00', '07h'),
    ('08:00:00', '08h'),
    ('09:00:00', '09h'),
    ('10:00:00', '10h'),
    ('11:00:00', '11h'),
    ('12:00:00', '12h'),
    ('13:00:00', '13h'),
    ('14:00:00', '14h'),
    ('15:00:00', '15h'),
    ('16:00:00', '16h'),
    ('17:00:00', '17h'),
    ('18:00:00', '18h'),
    ('19:00:00', '19h'),
    ('20:00:00', '20h'),
    ('21:00:00', '21h'),
    ('22:00:00', '22h'),
    ('23:00:00', '23h')
)

class DateTimeWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        widgets = (
            forms.TextInput(attrs={'class':'inm'}),
            forms.Select(choices=TIME_CHOICE, attrs={'class':'sells'}),
        )
        super(DateTimeWidget, self).__init__(widgets, *args, **kwargs)
    
    def decompress(self, value):
        if value:
            return [value.date(), value.strftime("%H:%M:%S")]
        return [None, None]
    

class DateTimeField(forms.MultiValueField):
    widget = DateTimeWidget
    
    def __init__(self, *args, **kwargs):
        fields = (
            forms.DateField(input_formats=['%d/%m/%Y', '%d-%m-%Y', '%d %m %Y', '%d %m %y', '%d/%m/%y', '%d-%m-%y']),
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
    approved = forms.BooleanField(required=True)
    preapproval_key = forms.CharField(required=True)
    currency_code = forms.CharField()
    starting_date = forms.DateTimeField(required=True)
    ending_date = forms.DateTimeField(required=True)
    max_total_amount_of_all_payments = forms.DecimalField(max_digits=8, decimal_places=2, required=True)
    sender_email = forms.CharField(required=True)
    status = forms.CharField(required=True)
    verify_sign = forms.CharField()
        
    def clean_sender_email(self):
        sender_email = self.cleaned_data['sender_email']
        if not Patron.objects.filter(paypal_email=sender_email).exists():
            raise ValidationError(_(u"Cette transaction ne semble pas lier à un compte interne"))
    

class PayIPNForm(forms.Form):
    action_type = forms.CharField(required=True)
    fees_payer = forms.CharField(required=True)
    pay_key = forms.CharField(required=True)
    payment_request_date = forms.DateTimeField(required=True)
    sender_email = forms.CharField(required=True)
    status = forms.CharField(required=True)
    
    def clean_sender_email(self):
        sender_email = self.cleaned_data['sender_email']
        if not Patron.objects.filter(paypal_email=sender_email).exists():
            raise ValidationError(_(u"Cette transaction ne semble pas lier à un compte interne"))
    

class BookingForm(forms.ModelForm):
    started_at = DateTimeField(required=True)
    ended_at = DateTimeField(required=True)
        
    class Meta:
        model = Booking
        fields = ('started_at', 'ended_at')
    
    def clean(self):
        started_at = self.cleaned_data.get('started_at', None)
        ended_at = self.cleaned_data.get('ended_at', None)
        
        product = self.instance.product
        if (started_at and ended_at):
            self.cleaned_data['total_amount'] = Booking.calculate_price(product, started_at, ended_at)
        return self.cleaned_data
    

class SinisterForm(forms.ModelForm):
    class Meta:
        model = Sinister
        fields = ('description',)
    
