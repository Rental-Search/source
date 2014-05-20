# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'clieninitialization/$', 'eloue.payments.slimpay_views.clientInitialization', name='slimpay_clieninitialization'),
	url(r'return_initial/$', 'eloue.payments.slimpay_views.return_initial', name='slimpay_return_intial'),
	url(r'notify/$', 'eloue.payments.slimpay_views.notify_response', name='slimpay_notify'),
)