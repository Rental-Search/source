from django.conf.urls import patterns, url
from accounts.admin_views import patron_create_subscription

urlpatterns = patterns('',
	url(r'^accounts/new_subscription/$', patron_create_subscription, name='patron_create_subscription'),
)