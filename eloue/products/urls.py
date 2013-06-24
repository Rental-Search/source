# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

from eloue.products.search_indexes import alert_search, product_search

from eloue.products.views import product_create, product_edit, message_create, reply_product_related_message, \
    product_delete, alert_create, alert_inform, alert_delete
from eloue.products.views import ProductList, AlertInformSuccess, AlertList
from eloue.rent.views import booking_create, booking_price, product_occupied_date, booking_create_redirect


urlpatterns = patterns('',
    url(r'^%s/$' % _("service_de_livraison"), 'eloue.products.views.shipping_service_offer', name="shipping_service_offer"),
    url(r'^%s/$' % _("ajouter"), 'eloue.products.views.publish_new_ad', name="publish_new_ad"),
    url(r'^%s/%s/$' % (_("ajouter"), _("objet")), product_create, name="product_create"),
    url(r'^%s/%s/$' % (_("ajouter"), _("voiture")), 'eloue.products.views.car_product_create', name="car_product_create"),
    url(r'^%s/%s/$' % (_("ajouter"), _("logement")), 'eloue.products.views.real_estate_product_create', name="real_estate_product_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/delete/$', product_delete, name="product_delete"),
	url(r'^%s/$' % _("alertes"), AlertList.as_view(), {'sqs': alert_search}, name="alert_list"),
	url(r'^%s/$' % _("alertes/ajouter"), alert_create, name="alert_create"),
	url(r'^%s/(?P<alert_id>\d+)/$' % _("alertes"), alert_inform, name="alert_inform"),
	url(r'^%s/(?P<alert_id>\d+)/$' % _("alertes/supprimer"), alert_delete, name="alert_delete"),
	url(r'^alertes/success/(?P<alert_id>\d+)/$', AlertInformSuccess.as_view(), name="alert_inform_success"),
    url(r'^(?P<product_id>\d+)/%s/(?P<recipient_id>\d+)/$' % _("nouveau-message"), message_create, name="message_create"),
    url(r'^(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', booking_create_redirect),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/price/$', booking_price, name="booking_price"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', booking_create, name="booking_create"),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<product_id>\d+)/occupied_date/$', product_occupied_date, name="product_occupied_date"),
    url(r'^([^/].+/)?$', ProductList.as_view(), {'sqs': product_search}, name="product_list"),
)
