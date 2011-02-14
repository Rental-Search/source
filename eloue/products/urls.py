# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

from eloue.products.search_indexes import product_search
from eloue.products.views import product_create, product_list, product_edit
from eloue.rent.views import booking_create, booking_price


urlpatterns = patterns('',
    url(r'^%s/$' % _("ajouter"), product_create, name="product_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/edit/$', product_edit, name="product_edit"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/price/$', booking_price, name="booking_price"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', booking_create, name="booking_create"),
    url(r'^([^/].+/)?$', product_list, {'sqs': product_search}, name="product_list"),
)
