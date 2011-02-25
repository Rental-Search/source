# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

from eloue.products.search_indexes import alert_search, product_search
from eloue.products.views import product_create, product_list, product_edit, alert_list, alert_create, alert_inform
from eloue.rent.views import booking_create, booking_price


urlpatterns = patterns('',
    url(r'^%s/$' % _("ajouter"), product_create, name="product_create"),
	url(r'^%s/$' % _("alertes"), alert_list, {'sqs': alert_search}, name="alert_list"),
	url(r'^%s/$' % _("alertes/ajouter"), alert_create, name="alert_create"),
	url(r'^%s/(?P<alert_id>\d+)/$' % _("alertes"), alert_inform, name="alert_inform"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/edit/$', product_edit, name="product_edit"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/price/$', booking_price, name="booking_price"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', booking_create, name="booking_create"),
    url(r'^([^/].+/)?$', product_list, {'sqs': product_search}, name="product_list"),
)
