# -*- coding: utf-8 -*-
import urlparse

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape

register = template.Library()

@register.filter
@stringfilter
def hostname(value):
    data = urlparse.urlsplit(value)
    return urlparse.urlunsplit(None, data[1], data[2], None, None) if data[2].strip('/') else escape(data[1])
hostname.is_safe = True
