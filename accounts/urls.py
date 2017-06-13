# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views import PatronDetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)(?:/page/(?P<page>\d+))?/$',
        PatronDetailView.as_view(), name='patron_detail'),
    url(r'^(?P<slug>[-\w]+)-(?P<patron_id>\d+)/$',
        PatronDetailView.as_view(), name="patron_detail_compat"),
)
