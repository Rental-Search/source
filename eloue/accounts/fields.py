# -*- coding: utf-8 -*-
import re

from django.forms.fields import Field
from django.utils.encoding import smart_unicode

DIGITS_ONLY = re.compile('(\(\d\)|[^\d+])')

class PhoneNumberField(Field):
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
        """
        if not value:
            return u''
        return re.sub(DIGITS_ONLY, '', smart_unicode(value))
    
