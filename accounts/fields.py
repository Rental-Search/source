# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import datetime
import calendar

from django import forms
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

from eloue import legacy

from .widgets import (
    MONTH_CHOICES, YEAR_CHOICES,
    ExpirationWidget, HiddenExpirationWidget, DateSelectWidget
)

DIGITS_ONLY = re.compile(r'(\(\d\)|[^\d+])', re.U)


class PhoneNumberField(forms.Field):
    def to_python(self, value):
        """
        >>> field = PhoneNumberField()
        >>> field.to_python("09 53 87 02 96")
        u'0953870296'
        >>> field.to_python("09.53.87.02.96")
        u'0953870296'
        >>> field.to_python("+33 9 53 87 02 96")
        u'+33953870296'
        >>> field.to_python("+33 (0) 9 53 87 02 96")
        u'+33953870296'
        >>> field.to_python("732-757-2923")
        u'7327572923'
        >>> field.to_python(None)
        u''
        """
        if not value:
            return u''
        res = DIGITS_ONLY.sub('', smart_unicode(value))
        if not res and value:
            raise forms.ValidationError(_(u'Vous devez spécifiez un numéro de téléphone'))
        return res


class CreditCardField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(CreditCardField, self).__init__(
            *args, min_length=16, max_length=24, **kwargs)

    def clean(self, value):
        def _luhn_valid(card_number):
            return sum(
                int(j) if not i%2 else sum(int(k) for k in str(2*int(j))) 
                for i, j 
                in enumerate(reversed(card_number))
            )%10 == 0
        value = super(CreditCardField, self).clean(value)
        if not value:
            return value
        card_number = value.replace(' ','').replace('-', '')
        try:
            if not _luhn_valid(card_number):
                raise forms.ValidationError(u'Veuillez verifier le numero de votre carte bancaire')
        except ValueError:
            raise forms.ValidationError(u'Votre numero doit etre composé uniquement de chiffres')
        return card_number


class ExpirationField(forms.MultiValueField):
    widget = ExpirationWidget
    hidden_widget = HiddenExpirationWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=MONTH_CHOICES, required=True),
            forms.ChoiceField(choices=YEAR_CHOICES, required=True),
        )
        super(ExpirationField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return ''.join(data_list)


class DateSelectField(forms.MultiValueField):
    DAYS = [('', 'Jour')] + [(x, x) for x in xrange(1, 32)]
    MONTHS = [('', 'Mois')] + [(x, _(calendar.month_name[x])) for x in xrange(1, 13)]

    def __init__(self, min_year=1900, max_year=2012, *args, **kwargs):
        self.YEARS = [('', 'Année')] + [(x, x) for x in xrange(max_year, min_year, -1)]
        fields = (
            legacy.TypedChoiceField(coerce=int, choices=self.DAYS),
            legacy.TypedChoiceField(coerce=int, choices=self.MONTHS),
            legacy.TypedChoiceField(coerce=int, choices=self.YEARS),
        )
        self.widget = DateSelectWidget(widgets=[field.widget for field in fields])
        self.hidden_widget = DateSelectWidget(widgets=[field.hidden_widget for field in fields])
        self.hidden_widget.is_hidden = True
        return super(DateSelectField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if len(data_list) != len(filter(None, data_list)):
            raise forms.ValidationError('')
        return datetime.date(year=data_list[2], month=data_list[1], day=data_list[0])

