# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe
from django.utils.formats import get_format

register = Library()

from products.models import UNIT


@register.filter
@stringfilter
def truncate(value, max_length):
    """
    >>> truncate("this is a text sample", 21)
    u'this is a text sample'
    >>> truncate("this is a text sample", 18)
    u'this is a text...'
    >>> truncate("this is a text sample", 14)
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
def nofollow(value):
    return "sources" in value.id


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
    from eloue.utils import currency
    return currency(value)


@register.simple_tag
def currency_symbol():
    """
    >>> settings.CONVERT_XPF = True
    >>> currency_symbol()
    u'XPF'
    >>> settings.CONVERT_XPF = False
    """
    if settings.CONVERT_XPF:
        return u"XPF"
    return get_format('CURRENCY_SYMBOL')


@register.filter
def partition(iterator, n):
    """
    Break a list into ``n`` pieces. The last list may be larger than the rest if
    the list doesn't break cleanly. That is::
        
        >>> l = range(10)
        
        >>> partition(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
        
        >>> partition(l, 3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]
        
        >>> partition(l, 4)
        [[0, 1], [2, 3], [4, 5], [6, 7, 8, 9]]
        
        >>> partition(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    
    """
    try:
        n = int(n)
        iterator = list(iterator)
    except (ValueError, TypeError):
        return [iterator]
    p = len(iterator) / n
    return [iterator[p * i:p * (i + 1)] for i in range(n - 1)] + [iterator[p * (i + 1):]]
