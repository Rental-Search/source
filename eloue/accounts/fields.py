# -*- coding: utf-8 -*-
import re
import datetime

from django import forms
from django.core import validators
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

DIGITS_ONLY = re.compile('(\(\d\)|[^\d+])')


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
        return re.sub(DIGITS_ONLY, '', smart_unicode(value))
    

MONTH_CHOICES = (
    ('01', '01'),
    ('02', '02'),
    ('03', '03'),
    ('04', '04'),
    ('05', '05'),
    ('06', '06'),
    ('07', '07'),
    ('08', '08'),
    ('09', '09'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12')
)

YEAR_CHOICES = [(lambda x: (x, x))(str(datetime.date.today().year+y)[2:]) for y in xrange(11)]



class ExpirationWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return (value[:2], value[2:])
        return (None, None)
    def __init__(self):
        widgets = (
            forms.Select(choices=MONTH_CHOICES),
            forms.Select(choices=YEAR_CHOICES),
            )
        super(ExpirationWidget, self).__init__(widgets)

class HiddenExpirationWidget(ExpirationWidget):
    def __init__(self):
        widgets = (
            forms.Select(choices=MONTH_CHOICES),
            forms.Select(choices=YEAR_CHOICES),
            )
        super(ExpirationWidget, self).__init__(widgets)

class ExpirationField(forms.MultiValueField):
    widget = ExpirationWidget
    hidden_widget = HiddenExpirationWidget
    default_error_messages = {
        'invalid_month': _(u'Month should be between 1 and 12.'),
        'invalid_year': _(u'Year yould be in the next 10 years.')
    }
    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=MONTH_CHOICES),
            forms.ChoiceField(choices=YEAR_CHOICES),
        )
        super(ExpirationField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[0] in validators.EMPTY_VALUES:
                raise ValidationError()
            if data_list[1] in validators.EMPTY_VALUES:
                raise ValidationError('')
            return ''.join(data_list)
        return None


import itertools
import string

mapping = dict(zip(string.ascii_uppercase, itertools.cycle('123456789')))

def rib_check(rib, generate_checksum=False):
    rib = rib.replace(' ', '')
    return not (89*int(rib[:5]) + 15*int(rib[5:10]) + 3*int(rib[10:21]) + int(rib[21:23]))%97

class RIBWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return [value[:5], value[5:10], value[10:21], value[21:23]]
        return [None, None, None, None]
    
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={'maxlength': 5, 'placeholder': _(u'code banque')}),
            forms.TextInput(attrs={'maxlength': 5, 'placeholder': _(u'code guichet')}),
            forms.TextInput(attrs={'maxlength': 11, 'placeholder': _(u'numéro de compte')}), 
            forms.TextInput(attrs={'maxlength': 2, 'placeholder':_(u'clé RIB')}),
        ]
        super(RIBWidget, self).__init__(widgets)

class HiddenRIBWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return [value[:5], value[5:10], value[10:21], value[21:23]]
        return [None, None, None, None]
    
    def __init__(self, attrs=None):
        widgets = [
            forms.HiddenInput,
            forms.HiddenInput,
            forms.HiddenInput, 
            forms.HiddenInput,
        ]
        super(RIBWidget, self).__init__(widgets)

class RIBField(forms.MultiValueField):
    widget = RIBWidget
    hidden_widget = HiddenRIBWidget
    default_error_messages = {
        'invalid_rib': _(u'Your RIB failed the checksum validation. Please verify.')
    }
    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(min_length=5, max_length=5),
            forms.CharField(min_length=5, max_length=5),
            forms.CharField(min_length=11, max_length=11),
            forms.CharField(min_length=2, max_length=2),
        )
        super(RIBField, self).__init__(fields, *args, **kwargs)

    def clean(self, value):
        out = super(RIBField, self).clean(value)
        if out:
            out = out.upper()
        if not rib_check(out):
            raise forms.ValidationError(self.error_messages['invalid_rib'])
        return out

    def compress(self, data_list):
        if data_list:
            return ''.join(data_list)
        return None
