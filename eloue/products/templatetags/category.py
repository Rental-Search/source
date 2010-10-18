# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library

from eloue.products.models import Category

register = Library()

@register.filter
def category(value):
    category = cache.get('category:%s' % value)
    if category is None:
        try:
            category = Category.objects.get(slug=value)
        except Category.DoesNotExist:
            category = 'None'
        cache.add('category:%s' % value, category, 0)
    return category


class Node(object):
    def __init__(self, value, count, childrens=[]):
        self.value = value
        self.count = count
        self.childrens = childrens
        
    def __repr__(self):
        return repr("%r (%r) : %r" % (self.value, self.count, self.childrens))
    

@register.filter
def build_tree(value):
    facets = dict([ (name, count) for name, count in value ])
    group = {}
    for category in Category.objects.filter(parent__isnull=True, slug__in=facets.keys()):
        if category.slug in facets.keys():
            group[category] = category.childrens.filter(slug__in=facets.keys())
    return group
