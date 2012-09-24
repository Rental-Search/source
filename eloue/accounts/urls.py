# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.accounts.views import PatronDetail


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)-(?P<patron_id>\d+)/$', PatronDetail.as_view(), name="patron_detail_compat"),
    url(r'^(?P<slug>[-\w]+)/$', PatronDetail.as_view(), name="patron_detail"),
    url(r'^(?P<recipient_username>[-\w]+)/message/$', 'eloue.products.views.patron_message_create', name='patron_message_create'),
    url(r'^(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', PatronDetail.as_view(), name="patron_detail"),
)
