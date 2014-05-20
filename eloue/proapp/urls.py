from django.conf import settings
from django.conf.urls import patterns, url, include

from eloue.proapp.api.resources import api_v1


urlpatterns = patterns('',
    url(r'api/', include(api_v1.urls)),
    url(r'dashboard/', 'eloue.proapp.views.proapp_dashboard', name='proapp_dashboard'),
)
