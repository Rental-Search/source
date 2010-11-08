# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library

from eloue.products.models import Category

register = Library()


@register.filter
def category(value):
    """
    >>> obj = category('parc')
    >>> obj.slug
    u'parc'
    >>> obj.name
    u'Parc'
    >>> category('porc')
    'None'
    """
    category = cache.get('category:%s' % value)
    if category is None:
        try:
            category = Category.objects.get(slug=value)
        except Category.DoesNotExist:
            category = 'None'
        cache.add('category:%s' % value, category, 0)
    return category
