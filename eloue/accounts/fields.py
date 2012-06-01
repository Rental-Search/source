# -*- coding: utf-8 -*-
import re
import datetime
import itertools
import string
import calendar

from django import forms
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
    ('', _(u'Mois')),
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

YEAR_CHOICES = [('', _(u'Année'))] + [(lambda x: (str(x)[2:], x))(datetime.date.today().year+y) for y in xrange(11)] 


class ExpirationWidget(forms.MultiWidget):
    def __init__(self):
        widgets = (
            forms.Select(choices=MONTH_CHOICES),
            forms.Select(choices=YEAR_CHOICES),
            )
        super(ExpirationWidget, self).__init__(widgets)
    
    def decompress(self, value):
        return (value[:2], value[2:])

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

    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=MONTH_CHOICES, required=True),
            forms.ChoiceField(choices=YEAR_CHOICES, required=True),
        )
        super(ExpirationField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return ''.join(data_list)


mapping = dict(zip(string.ascii_uppercase, itertools.cycle('123456789')))


def rib_check(rib):
    rib = rib.replace(' ', '')
    rib = ''.join((mapping.get(ch, ch) for ch in rib))
    return (89*int(rib[:5]) + 15*int(rib[5:10]) + 3*int(rib[10:21]) + int(rib[21:23]))%97 == 0


class RIBWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={'maxlength': 5 }),
            forms.TextInput(attrs={'maxlength': 5 }),
            forms.TextInput(attrs={'maxlength': 11 }), 
            forms.TextInput(attrs={'maxlength': 2 }),
        ]
        super(RIBWidget, self).__init__(widgets)

    def decompress(self, value):
        value = value.replace(' ', '')
        if value:
            return (value[:5], value[5:10], value[10:21], value[21:23])
        return (None, None, None, None)


class HiddenRIBWidget(RIBWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.HiddenInput,
            forms.HiddenInput,
            forms.HiddenInput, 
            forms.HiddenInput,
        ]
        super(HiddenRIBWidget, self).__init__(widgets)


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
        value = super(RIBField, self).clean(value).upper()
        if not rib_check(value):
            raise forms.ValidationError(self.error_messages['invalid_rib'])
        return value

    def compress(self, data_list):
        return ''.join(data_list)


class DateSelectWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return (value.day, value.month, value.year)
        return (None, None, None)
    def __call__(self):
        return self

class DateSelectField(forms.MultiValueField):
    DAYS = [('', 'Jour')] + [(x, x) for x in xrange(1, 32)]
    MONTHS = [('', 'Mois')] + [(x, _(calendar.month_name[x])) for x in xrange(1, 13)]

    def __init__(self, min_year=1900, max_year=2012, *args, **kwargs):
        self.YEARS = [('', 'Année')] + [(x, x) for x in xrange(max_year, min_year, -1)]
        fields = (
            forms.TypedChoiceField(coerce=int, choices=self.DAYS),
            forms.TypedChoiceField(coerce=int, choices=self.MONTHS),
            forms.TypedChoiceField(coerce=int, choices=self.YEARS),
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

