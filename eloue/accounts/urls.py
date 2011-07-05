# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.accounts.views import patron_detail


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)-(?P<patron_id>\d+)/$', patron_detail, name="patron_detail_compat"),
    url(r'^(?P<slug>[-\w]+)/$', patron_detail, name="patron_detail"),
    url(r'^(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', patron_detail, name="patron_detail"),
)
