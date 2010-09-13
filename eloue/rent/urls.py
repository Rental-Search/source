# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.rent.views import preapproval_ipn, pay_ipn

urlpatterns = patterns('',
    url(r'^ipn/preapproval/$', preapproval_ipn, name="preapproval_ipn"),
    url(r'^ipn/pay/$', pay_ipn, name="pay_ipn")
)
