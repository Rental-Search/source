# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.utils.translation import ugettext as _

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

YEAR_CHOICES = [('', _(u'Année'))] + [(lambda x: (str(x)[2:], x))(date.today().year+y) for y in xrange(11)] 


class ExpirationWidget(forms.MultiWidget):
    def __init__(self):
        widgets = (
            forms.Select(choices=MONTH_CHOICES),
            forms.Select(choices=YEAR_CHOICES),
            )
        super(ExpirationWidget, self).__init__(widgets)
    
    def decompress(self, value):
        if value is None:
            return (None, None)
        return (value[:2], value[2:])

class HiddenExpirationWidget(ExpirationWidget):
    def __init__(self):
        widgets = (
            forms.Select(choices=MONTH_CHOICES),
            forms.Select(choices=YEAR_CHOICES),
            )
        super(ExpirationWidget, self).__init__(widgets)


class DateSelectWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return (value.day, value.month, value.year)
        return (None, None, None)
    def __call__(self):
        return self


class CommentedCheckboxInput(forms.CheckboxInput):

    def __init__(self, info_text, attrs=None, check_test=bool):
        super(CommentedCheckboxInput, self).__init__(attrs, check_test)
        from django.utils.html import escape
        self.info_text = escape(info_text)

    def render(self, name, value, attrs=None):
        from django.utils.safestring import mark_safe
        return mark_safe('<label class="checkbox">' + super(CommentedCheckboxInput, self).render(name, value, attrs) + '\t' + self.info_text + '</label>')
