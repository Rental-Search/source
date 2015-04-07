# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from products.helpers import calculate_available_quantity

from .models import Booking, Sinister
from .utils import DATE_TIME_FORMAT

BOOKING_DAYS = getattr(settings, 'BOOKING_DAYS', 85)


class SinisterForm(forms.ModelForm):
    class Meta:
        model = Sinister
        fields = ('description',)


class BookingForm(forms.ModelForm):
    started_at = forms.DateTimeField(required=True, input_formats=DATE_TIME_FORMAT)
    ended_at = forms.DateTimeField(required=True, input_formats=DATE_TIME_FORMAT)
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
        # TODO: Validation for api is slightly different than validation for form.
        # TODO: Api action should be rewritten to not use form at all.
        super(BookingForm, self).clean()
        started_at = self.cleaned_data.get('started_at')
        ended_at = self.cleaned_data.get('ended_at')
        quantity = self.cleaned_data.get('quantity')

        product = self.instance.product

        if started_at and ended_at:
            self.max_available = calculate_available_quantity(product, started_at, ended_at)

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
