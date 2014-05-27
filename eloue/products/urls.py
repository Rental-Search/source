# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

from products.search_indexes import alert_search, product_search

from products.views import product_create, message_create, \
    product_delete, alert_create, alert_inform, alert_delete
from products.views import ProductList, AlertInformSuccess, AlertList
from rent.views import booking_create, booking_price, product_occupied_date, \
    booking_create_redirect, phone_create


urlpatterns = patterns('',
    url(r'^%s/$' % _("service_de_livraison"), 'products.views.shipping_service_offer', name="shipping_service_offer"),
    url(r'^%s/$' % _("ajouter"), 'products.views.publish_new_ad', name="publish_new_ad"),
    url(r'^%s/$' % _("deposer"), 'products.views.publish_new_ad2', name="publish_new_ad2"),
    url(r'^%s/%s/$' % (_("ajouter"), _("objet")), product_create, name="product_create"),
    url(r'^%s/%s/$' % (_("ajouter"), _("voiture")), 'products.views.car_product_create', name="car_product_create"),
    url(r'^%s/%s/$' % (_("ajouter"), _("logement")), 'products.views.real_estate_product_create', name="real_estate_product_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/delete/$', product_delete, name="product_delete"),
	url(r'^%s/$' % _("alertes"), AlertList.as_view(), {'sqs': alert_search}, name="alert_list"),
	url(r'^%s/$' % _("alertes/ajouter"), alert_create, name="alert_create"),
	url(r'^%s/(?P<alert_id>\d+)/$' % _("alertes"), alert_inform, name="alert_inform"),
	url(r'^%s/(?P<alert_id>\d+)/$' % _("alertes/supprimer"), alert_delete, name="alert_delete"),
	url(r'^alertes/success/(?P<alert_id>\d+)/$', AlertInformSuccess.as_view(), name="alert_inform_success"),
    url(r'^(?P<product_id>\d+)/%s/(?P<recipient_id>\d+)/$' % _("nouveau-message"), message_create, name="message_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', booking_create_redirect, name='booking_create_redirect'),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/price/$', booking_price, name="booking_price"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', booking_create, name="booking_create"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/occupied_date/$', product_occupied_date, name="product_occupied_date"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/appeler/$', phone_create, name="phone_create"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/appeler/occupied_date/$', product_occupied_date, name="product_occupied_date"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/appeler/price/$', booking_price, name="booking_price"),
    url(r'^([^/].+/)?$', ProductList.as_view(), {'sqs': product_search}, name="product_list"),
)
