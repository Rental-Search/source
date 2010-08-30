# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from haystack.query import SearchQuerySet

from eloue.products.views import product_detail, product_list

product_search = SearchQuerySet().facet('category').facet('owner')

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', product_detail, name="product_detail"),
    url(r'^([^/].+/)?$', product_list, { 'sqs':product_search }, name="product_list")
)
