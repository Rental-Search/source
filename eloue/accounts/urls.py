# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.accounts.views import create_account_ipn, patron_detail


urlpatterns = patterns('',
    url(r'^ipn/$', create_account_ipn, name="create_account_ipn"),
    url(r'^(?P<slug>[-\w]+)-(?P<patron_id>\d+)/$', patron_detail, name="patron_detail_compat"),
    url(r'^(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', patron_detail, name="patron_detail_page"),
    url(r'^(?P<slug>[-\w]+)/$', patron_detail, name="patron_detail")
)
