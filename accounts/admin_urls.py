from django.conf.urls import patterns, url
from accounts.admin_views import patron_create_subscription, add_iban

urlpatterns = patterns('',
	url(r'^accounts/new_subscription/$', patron_create_subscription, name='patron_create_subscription'),
	url(r'^accounts/slimpay/(?P<patron_id>\d+)/$', add_iban, name='add_iban'),
)