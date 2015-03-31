# -*- coding: utf-8 -*-

from collections import OrderedDict
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
        res = list(Category.on_site.filter(slug__in=value).order_by('lft').iterator())
        return res


@cached(timeout=0, key_func=simple_cache_key)
@register.filter
@split_args_dict
def ancestors(value, ascending=False, include_self=False, attr=None):
    if value is None:
        return []
    qs = value.get_ancestors(ascending=bool(ascending), include_self=bool(include_self in ('True', 'true', 1)))
    return qs if attr is None else [getattr(obj, attr) for obj in qs]


class FakeCategory(object):
    slug = None
    name = None
    _url = None

    def get_absolute_url(self):
        return self._url


@register.assignment_tag
def arrange_categories(categories_map, root_id):
    ids = categories_map.get(root_id, [])
    category_dict = dict(((x.id, x) for x in Category.on_site.filter(
        id__in=[i for i in ids if isinstance(i, int)])))

    categories = []
    for item in ids:
        if isinstance(item, (list, tuple)):
            cat = FakeCategory()
            cat.name, cat._url = tuple(item)
            categories.append(cat)
        else:
            try:
                categories.append(category_dict[item])
            except KeyError:
                pass
    return categories
