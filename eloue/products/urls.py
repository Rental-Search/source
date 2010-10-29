# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.products.search_indexes import product_search
from eloue.products.views import product_create, product_detail, product_list
from eloue.rent.views import booking_create


urlpatterns = patterns('',
    url(r'^ajouter/$', product_create, name="product_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/louer/$', booking_create, name="booking_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', product_detail, name="product_detail"),
    url(r'^([^/].+/)?$', product_list, { 'sqs':product_search }, name="product_list"),
)
