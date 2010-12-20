# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library

from eloue.products.models import Category

register = Library()


@register.filter
def category(value):
    category = cache.get('category:%s' % value)
    if not category:
        try:
            category = Category.objects.get(slug=value)
        except Category.DoesNotExist:
            category = 'None'
        cache.add('category:%s' % value, category)
    return category
