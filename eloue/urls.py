# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.sitemaps.views import index, sitemap

from eloue.sitemaps import FlatPageSitemap, PatronSitemap, ProductSitemap
from eloue.accounts.forms import EmailAuthenticationForm, EmailPasswordResetForm
from eloue.accounts.views import activate

log = logbook.Logger('eloue')

try:
    admin.autodiscover()
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e.message)

sitemaps = {
    'flatpages':FlatPageSitemap,
    'patrons':PatronSitemap,
    'products':ProductSitemap
}

urlpatterns = patterns('',
    url(r'^sitemap.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+).xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^reset/$', password_reset, {
        'is_admin_site':False,
        'password_reset_form':EmailPasswordResetForm,
        'template_name':'accounts/password_reset_form.html',
        'email_template_name':'accounts/password_reset_email.html'
        }, name="password_reset"),
    url(r'^reset/done/$', password_reset_done, {
        'template_name':'accounts/password_reset_done.html'
    }, name="password_reset_done"),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
        'template_name':'accounts/password_reset_confirm.html'
    }, name="password_reset_confirm"),
    url(r'^reset/complete/$', password_reset_complete, {
        'template_name':'accounts/password_reset_complete.html'
    }, name="password_reset_complete"),
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='auth_activate'),
    url(r'^login/$', login, {
        'template_name':'accounts/login.html',
        'authentication_form':EmailAuthenticationForm
    }, name='auth_login'),
    url(r'^logout/$', logout_then_login, name='auth_logout'),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^loueur/', include('eloue.accounts.urls')),
    url(r'^location/', include('eloue.products.urls')),
    url(r'^rent/', include('eloue.rent.urls')),
    url(r'^edit/', include(admin.site.urls)),
)
