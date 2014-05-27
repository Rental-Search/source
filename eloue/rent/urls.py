# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from rent.views import preapproval_ipn, pay_ipn
from rent.views import BookingSuccess, BookingFailure

urlpatterns = patterns('',
    url(r'^ipn/preapproval/$', preapproval_ipn, name="preapproval_ipn"),
    url(r'^ipn/pay/$', pay_ipn, name="pay_ipn"),
    url(r'^success/(?P<booking_id>[0-9a-f]{32})/$', BookingSuccess.as_view(), name="booking_success"),
    url(r'^cancel/(?P<booking_id>[0-9a-f]{32})/$', BookingFailure.as_view(), name="booking_failure"),
)
