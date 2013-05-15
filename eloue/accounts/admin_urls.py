from django.conf.urls.defaults import *
from eloue.accounts.admin_views import patron_create_subscription

urlpatterns = patterns('',
	url(r'^accounts/new_subscription/$', patron_create_subscription, name='patron_create_subscription'),
)