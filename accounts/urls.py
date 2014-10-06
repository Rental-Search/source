# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from accounts.views import PatronDetail


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)-(?P<patron_id>\d+)/$', PatronDetail.as_view(), name="patron_detail_compat"),
    url(r'^(?P<slug>[-\w]+)/$', PatronDetail.as_view(), name="patron_detail"),
    url(r'^(?P<recipient_username>[-\w]+)/message/$', 'products.views.patron_message_create', name='patron_message_create'),
    url(r'^(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', PatronDetail.as_view(), name="patron_detail"),
)


from accounts.views import PublicProfileView

ui3_urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', PublicProfileView.as_view(), name='public_profile'),
)
