# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.products.forms import ProductForm
from eloue.products.search_indexes import product_search
from eloue.products.views import product_create, product_detail, product_list
from eloue.products.wizard import ProductWizard
from eloue.rent.forms import BookingForm
from eloue.rent.wizard import BookingWizard


urlpatterns = patterns('',
    url(r'^ajouter/$', product_create, name="product_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/louer/$', BookingWizard([BookingForm,EmailAuthenticationForm]), name="product_rent"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', product_detail, name="product_detail"),
    url(r'^([^/].+/)?$', product_list, { 'sqs':product_search }, name="product_list"),
)
