# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.rent.views import preapproval_ipn, pay_ipn, booking_success, booking_failure, fake_preapproval_ipn, fake_pay_ipn

urlpatterns = patterns('',
    url(r'^ipn/preapproval/$', preapproval_ipn, name="preapproval_ipn"),
    url(r'^ipn/fakepreapproval/$', fake_preapproval_ipn, name="fake_preapproval_ipn"),
    url(r'^ipn/pay/$', pay_ipn, name="pay_ipn"),
    url(r'^ipn/fakepay/$', fake_pay_ipn, name="fake_pay_ipn"),
    url(r'^success/(?P<booking_id>[0-9a-f]{32})/$', booking_success, name="booking_success"),
    url(r'^cancel/(?P<booking_id>[0-9a-f]{32})/$', booking_failure, name="booking_failure"),
)
