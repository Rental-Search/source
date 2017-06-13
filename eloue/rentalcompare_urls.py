# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url

from products.models import Product
from eloue.views import ImportedObjectRedirectView
from accounts.models import Patron

urlpatterns = patterns('',
                       
    url(r'^rent/(?P<original_slug>[-\w]+)/(?P<original_id>[\d]+)/$', 
        ImportedObjectRedirectView.as_view(origin="rentalcompare.com", 
                                           model=Product,
                                           fallback_pattern_name="product_list"), 
        name='product_detail_rentalcompare'),
                       
    url(r'^inventory/(?P<username>[\w@\.]+)/$', 
        ImportedObjectRedirectView.as_view(origin="rentalcompare.com", 
                                           model=Patron,
                                           fallback_pattern_name="product_list",
                                           # See import_rentalcompare command
                                           filter_key="username",
                                           convert=lambda username: username[:30]), 
        name='patron_detail_rentalcompare'),

)
