from django.conf.urls.defaults import *
from eloue.reporting.admin_views import stats


urlpatterns = patterns('',
    url(r'^all/$', stats, name="stats")
)