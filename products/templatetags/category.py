# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.itercompat import is_iterable

from products.models import Category
from eloue.decorators import split_args_dict, cached
from eloue.utils import simple_cache_key

register = Library()


@cached(timeout=0, key_func=simple_cache_key)
@register.filter
def category(value):
    if value is None:
        return None
    if isinstance(value, basestring):
        try:
            return Category.on_site.get(slug=value)
        except Category.DoesNotExist:
            return
    if is_iterable(value):
        res = list(Category.on_site.filter(slug__in=value).iterator())
        index = value.index
        res.sort(key=lambda obj: index(obj.slug))
        return res


@cached(timeout=0, key_func=simple_cache_key)
@register.filter
@split_args_dict
def ancestors(value, ascending=False, include_self=False, attr=None):
    if value is None:
        return []
    qs = value.get_ancestors(ascending=bool(ascending), include_self=bool(include_self in ('True', 'true', 1)))
    return qs if attr is None else [getattr(obj, attr) for obj in qs]
