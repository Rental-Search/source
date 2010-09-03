# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.rent.view import ipn_handler

urlpatterns = patterns('',
    url(r'^ipn/$', ipn_handler, name="ipn_handler")
)
