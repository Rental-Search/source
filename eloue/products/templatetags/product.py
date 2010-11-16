# -*- coding: utf-8 -*-
import re

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe

register = Library()

from eloue.products.models import CURRENCY, UNIT


@register.filter
@stringfilter
def truncate(value, max_length):
    """
    >>> truncate("this is a text sample", 21)
    u'this is a text sample'
    >>> truncate("this is a text sample", 18)
    u'this is a text...'
    >>> truncate("this is a text sample", 15)
    u'this is a text...'
    """
    if len(value) <= max_length:
        return value
    truncated = value[:max_length]
    if value[max_length] != " ":
        rightmost_space = truncated.rfind(" ")
        if rightmost_space != -1:
            truncated = truncated[:rightmost_space]
    return "%s..." % truncated


@register.filter
@stringfilter
def capitalize(value):
    """
    >>> capitalize(u"BONJOUR")
    u'Bonjour'
    >>> capitalize(u"bonjour")
    u'Bonjour'
    """
    return value.capitalize()


@register.filter
@stringfilter
def linebreaksp(value, autoescape=None):
    def linebreaks(value, autoescape=None):
        value = re.sub(r'\r\n|\r|\n', '\n', force_unicode(value))  # normalize newlines
        paras = re.split('\n', value)
        if autoescape:
            paras = [u'<p>%s</p>' % escape(p.strip()) for p in paras]
        else:
            paras = [u'<p>%s</p>' % p.strip() for p in paras]
        return u'\n\n'.join(paras)
    autoescape = autoescape and not isinstance(value, SafeData)
    return mark_safe(linebreaks(value, autoescape))
linebreaksp.is_safe = True
linebreaksp.needs_autoescape = True


@register.filter
@stringfilter
def unit(value):
    """
    >>> unit(1)
    u'jour'
    """
    return UNIT[int(value)][1]


@register.filter
@stringfilter
def currency(value):
    """
    >>> currency('USD')
    u'$'
    """
    for name, symbol in CURRENCY:
        if name == value:
            return symbol

