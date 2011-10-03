# -*- coding: utf-8 -*-
import datetime
import logbook

from dateutil import parser

from django import forms
from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from pyke.knowledge_engine import CanNotProve

from eloue.rent.models import Booking, Sinister
from eloue.rent.utils import get_product_occupied_date, datespan, DATE_FORMAT
from django.db.models import Q

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

BOOKING_DAYS = getattr(settings, 'BOOKING_DAYS', 85)


class ISO8601DateTimeField(forms.Field):
    def to_python(self, value):
        return parser.parse(value)
    

class DateTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None, *args, **kwargs):
        widgets = (
            forms.DateInput(attrs={'class': 'ins dps'}, format=date_format),
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
    approved = forms.TypedChoiceField(required=True, coerce=lambda x: x == 'true', choices=(('true', 'True'), ('false', 'False')))
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
    
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        initial = kwargs['initial']
        started_at = initial['started_at']
        ended_at = initial['ended_at']
        product = self.instance.product
        self.fields['quantity'] = forms.IntegerField(widget=forms.Select(choices=enumerate(xrange(1, 1 + Booking.calculate_available_quantity(
                                                        product, 
                                                        datetime.datetime.strptime(' '.join(started_at), "%d/%m/%Y %H:%M:%S"), 
                                                        datetime.datetime.strptime(' '.join(ended_at), "%d/%m/%Y %H:%M:%S")
                                                    )), start=1)))
        
    class Meta:
        model = Booking
        fields = ('started_at', 'ended_at', 'quantity')
    
    def clean(self):
        started_at = self.cleaned_data.get('started_at', None)
        ended_at = self.cleaned_data.get('ended_at', None)
        quantity = self.cleaned_data.get('quantity')

        product = self.instance.product
        bookings = Booking.objects.filter(product=product).filter(Q(state="pending")|Q(state="ongoing"))
        booked_dates = get_product_occupied_date(bookings)
        if (quantity > Booking.calculate_available_quantity(product, started_at, ended_at)): 
            raise ValidationError(_(u'Pas assez de produit disponible'))
        if (started_at and ended_at):
            try:
                self.cleaned_data['total_amount'] = Booking.calculate_price(product, started_at, ended_at)[1]
            except CanNotProve:
                raise ValidationError(_(u"Vous ne pouvez pas louer cet objet pour ces dates"))
            
            booking_dates = datespan(started_at, ended_at)
            if started_at <= datetime.datetime.now() or ended_at <= datetime.datetime.now():
                raise ValidationError(_(u"Vous ne pouvez pas louer à ces dates"))
            if started_at >= ended_at:
                raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))
            if (ended_at - started_at) > datetime.timedelta(days=BOOKING_DAYS):
                raise ValidationError(_(u"La durée d'une location est limitée à %s jours."%BOOKING_DAYS))
            if set(booked_dates) & set(booking_dates):
                raise ValidationError(_(u"Ces dates sont déjà prises pour ce produit."))
        return self.cleaned_data
    

class BookingConfirmationForm(forms.Form):
    pass


class BookingStateForm(forms.ModelForm):
    state = forms.ChoiceField(choices=Booking.STATE, widget=forms.HiddenInput())
    
    class Meta:
        model = Booking
        fields = ('state',)
    

class SinisterForm(forms.ModelForm):
    class Meta:
        model = Sinister
        fields = ('description',)
    

class IncidentForm(forms.Form):
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={'placeholder': _(u"Décrivez votre incident")}))
