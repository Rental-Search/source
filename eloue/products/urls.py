# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.products.forms import ProductForm
from eloue.products.search_indexes import product_search
from eloue.products.views import product_detail, product_list
from eloue.products.wizard import ProductWizard

urlpatterns = patterns('',
    url(r'^ajouter/$', ProductWizard([ProductForm, EmailAuthenticationForm]), name="product_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', product_detail, name="product_detail"),
    url(r'^([^/].+/)?$', product_list, { 'sqs':product_search }, name="product_list"),
)
