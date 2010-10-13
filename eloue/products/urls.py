# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.products.search_indexes import product_search
from eloue.products.views import product_detail, product_list

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', product_detail, name="product_detail"),
    url(r'^([^/].+/)?$', product_list, { 'sqs':product_search }, name="product_list")
)
