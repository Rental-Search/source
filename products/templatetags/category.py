# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library

from products.models import Category
from eloue.decorators import split_args_dict

register = Library()


@register.filter
def category(value):
    category = cache.get('category:%s' % value)
    if not category:
        try:
            category = Category.on_site.get(slug=value)
        except Category.DoesNotExist:
            category = 'None'
        cache.set('category:%s' % value, category, 0)
    return category


@register.filter
@split_args_dict
def ancestors(value, ascending=False, include_self=False):
    return value.get_ancestors(ascending=bool(ascending), include_self=bool(include_self))
