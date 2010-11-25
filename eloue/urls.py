# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.sitemaps.views import index, sitemap

from eloue.accounts.forms import EmailPasswordResetForm
from eloue.accounts.views import activate, authenticate, authenticate_headless, dashboard, patron_edit, owner_booking, owner_history, \
    borrower_booking, borrower_history, patron_edit_password, patron_paypal, owner_product
from eloue.api import api_v1
from eloue.products.views import homepage
from eloue.rent.views import booking_detail, booking_accept, booking_reject, booking_incident, booking_close, booking_cancel
from eloue.sitemaps import FlatPageSitemap, PatronSitemap, ProductSitemap

log = logbook.Logger('eloue')

try:
    admin.autodiscover()
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)

sitemaps = {
    'flatpages': FlatPageSitemap,
    'patrons': PatronSitemap,
    'products': ProductSitemap
}

urlpatterns = patterns('',
    url(r'^sitemap.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+).xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^reset/$', password_reset, {
        'is_admin_site': False,
        'password_reset_form': EmailPasswordResetForm,
        'template_name': 'accounts/password_reset_form.html',
        'email_template_name': 'accounts/password_reset_email.html'
        }, name="password_reset"),
    url(r'^reset/done/$', password_reset_done, {
        'template_name': 'accounts/password_reset_done.html'
    }, name="password_reset_done"),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
        'template_name': 'accounts/password_reset_confirm.html'
    }, name="password_reset_confirm"),
    url(r'^reset/complete/$', password_reset_complete, {
        'template_name': 'accounts/password_reset_complete.html'
    }, name="password_reset_complete"),
    url(r'^faq/', include('faq.urls')),
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='auth_activate'),
    url(r'^login/$', authenticate, name='auth_login'),
    url(r'^login_headless/$', authenticate_headless, name='auth_login_headless'),
    url(r'^logout/$', logout_then_login, name='auth_logout'),
    url(r'^dashboard/$', dashboard, name="dashboard"),
    url(r'^dashboard/account/profile/$', patron_edit, name="patron_edit"),
    url(r'^dashboard/account/password/$', patron_edit_password, name="patron_edit_password"),
    url(r'^dashboard/account/paypal/$', patron_paypal, name="patron_paypal"),
    url(r'^dashboard/owner/booking/$', owner_booking, name="owner_booking"),
    url(r'^dashboard/owner/booking/page/(?P<page>\d+)/$', owner_booking, name="owner_booking"),
    url(r'^dashboard/owner/history/$', owner_history, name="owner_history"),
    url(r'^dashboard/owner/history/page/(?P<page>\d+)/$', owner_history, name="owner_history"),
    url(r'^dashboard/owner/product/$', owner_product, name="owner_product"),
    url(r'^dashboard/owner/product/page/(?P<page>\d+)/$', owner_product, name="owner_product"),
    url(r'^dashboard/borrower/booking/$', borrower_booking, name="borrower_booking"),
    url(r'^dashboard/borrower/booking/page/(?P<page>\d+)/$', borrower_booking, name="borrower_booking"),
    url(r'^dashboard/borrower/history/$', borrower_history, name="borrower_history"),
    url(r'^dashboard/borrower/history/page/(?P<page>\d+)/$', borrower_history, name="borrower_history"),
    url(r'^dashboard/booking/(?P<booking_id>[0-9a-f]{32})/$', booking_detail, name="booking_detail"),
    url(r'^dashboard/booking/(?P<booking_id>[0-9a-f]{32})/accept/$', booking_accept, name="booking_accept"),
    url(r'^dashboard/booking/(?P<booking_id>[0-9a-f]{32})/cancel/$', booking_cancel, name="booking_cancel"),
    url(r'^dashboard/booking/(?P<booking_id>[0-9a-f]{32})/reject/$', booking_reject, name="booking_reject"),
    url(r'^dashboard/booking/(?P<booking_id>[0-9a-f]{32})/incident/$', booking_incident, name="booking_incident"),
    url(r'^dashboard/booking/(?P<booking_id>[0-9a-f]{32})/close/$', booking_close, name="booking_close"),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^loueur/', include('eloue.accounts.urls')),
    url(r'^location/', include('eloue.products.urls')),
    url(r'^rent/', include('eloue.rent.urls')),
    url(r'^experiments/', include('django_lean.experiments.urls')),
    url(r'^edit/reports/', include('django_lean.experiments.admin_urls')),
    url(r'^edit/', include(admin.site.urls)),
    url(r'^api/', include(api_v1.urls)),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^$', homepage, name="home")
)
