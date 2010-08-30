# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.products.views import product_detail

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)-(?P<patron_id>\d+)/$', product_detail, name="product_detail"),
)
