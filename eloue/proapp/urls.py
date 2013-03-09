from django.conf import settings
from django.conf.urls.defaults import *

from eloue.proapp.api import api_v1


urlpatterns = patterns('',
    url(r'api/', include(api_v1.urls)),
)
