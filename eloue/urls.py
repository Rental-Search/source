# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

try:
    admin.autodiscover()
except admin.sites.AlreadyRegistered:
    pass # FIXME : Has been made to enable doctest, put logging in there

urlpatterns = patterns('',
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^edit/', include(admin.site.urls)),
)
