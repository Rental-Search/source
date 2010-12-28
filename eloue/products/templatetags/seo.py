# -*- coding: utf-8 -*-
import re

from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy

register = Library()


@register.filter
def striplinebreak(value):
    """Converts newlines into <p> and <br />s."""
    value = re.sub(r'\r\n|\r|\n', '\n', force_unicode(value)) # normalize newlines
    return mark_safe(re.sub(r'\n', '', value))
striplinebreak.is_safe = True
