# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin

from accounts.views import contact

log = logbook.Logger('eloue')

try:
    admin.autodiscover()
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)


urlpatterns = patterns('',
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', contact, name="contact"),
)
