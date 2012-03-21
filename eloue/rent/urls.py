# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.rent.views import booking_success, booking_failure

urlpatterns = patterns('',
    url(r'^success/(?P<booking_id>[0-9a-f]{32})/$', booking_success, name="booking_success"),
    url(r'^cancel/(?P<booking_id>[0-9a-f]{32})/$', booking_failure, name="booking_failure"),
)
