# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

from haystack.query import SearchQuerySet

from .models import Product

__all__ = ['product_search']


product_search = SearchQuerySet().models(Product) \
    .filter(is_archived=False) \
    .facet('sites').facet('categories').facet('owner').facet('price') \
    .narrow('sites:%s' % settings.SITE_ID)
