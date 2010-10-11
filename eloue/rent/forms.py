# -*- coding: utf-8 -*-
import logbook

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.rent.models import Booking

log = logbook.Logger('eloue.rent')

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
            raise ValidationError(_("Cette transaction ne semble pas lier à un compte interne"))
    

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
            raise ValidationError(_("Cette transaction ne semble pas lier à un compte interne"))
    

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
    
