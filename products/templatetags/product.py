# -*- coding: utf-8 -*-
import re
from itertools import islice
from datetime import timedelta, date
import calendar

from django.conf import settings
from django.template import Library, Node
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe
from django.utils.formats import get_format
from django.utils import six
from django.views.generic.dates import timezone_today

register = Library()

from products.choices import UNIT
from eloue.utils import currency
from eloue.decorators import split_args_int


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


@register.filter(name='currency')
@stringfilter
def currency_filter(value):
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


@register.filter
def location(obj, attrname='location'):
    """
    Retrieves object's location and returns it as a comma-separated string.
    
    >>> from django.contrib.gis.geos import Point
    >>> class Location(object): pass
    >>> obj = Location()
    >>> obj.location = Point(46.3, 2.11)
    >>> location(obj)
    '46.3, 2.11'
    
    """
    location = getattr(obj, attrname, None)
    return '%s, %s' % (location.x, location.y) if location else attrname


@register.filter
def takeby(iterator, size):
    """
    Breaks an iterator into parts by ``n`` items.
    The ending items may be ignored if there are less then ``n`` of them.
    That is::
        
        >>> l = range(10)
        
        >>> map(tuple, takeby(l, 5))
        [(0, 1, 2, 3, 4), (5, 6, 7, 8, 9)]
        
        >>> map(tuple, takeby(l, 3))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        
        >>> map(tuple, takeby(l, 2))
        [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
    
    """
    iterator = iter(iterator)
    parts = [iterator] * size
    return six.moves.zip(*parts)


@register.filter
@split_args_int
def takeby_transposed(iterator, size, max_length=None):
    """
    Breaks an iterator into parts by ``n`` items.
    The resulting parts may have different length if ``limit`` is not provided.
    That is::
        
        >>> l = range(10)
        
        >>> map(tuple, takeby_transposed(l, 3))
        [(0, 3, 6, 9), (1, 4, 7), (2, 5, 8)]
        
        >>> map(tuple, takeby_transposed(l, '3:9'))
        [(0, 3, 6), (1, 4, 7), (2, 5, 8)]
    
    """
    return (islice(iterator, start, max_length, size) for start in six.moves.range(size))


def next_month(a, b):
    value = a[-1]
    a.append(value + timedelta(days=calendar.monthrange(value.year, value.month)[1]))
    return a

class MonthCalendarNode(Node):
    count = 11

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        today = timezone_today()
        context.update({
            'today': today,
            'months': reduce(next_month, six.moves.range(self.count), [today]),
            'week_days': [date(2001, 1, 1 + i) for i in six.moves.range(7)], # January 1, 2001, was a Monday.
            'monthcalendar': calendar.monthcalendar(today.year, today.month),
        })
        return self.nodelist.render(context)

@register.tag('monthcalendar')
def do_monthcalendar(parser, token):
    nodelist = parser.parse(('endmonthcalendar',))
    parser.delete_first_token()
    tokens = token.split_contents()
    return MonthCalendarNode(nodelist)
