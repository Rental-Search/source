# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.sitemaps.views import index, sitemap
from django.utils import translation
from django.utils.translation import ugettext as _

from eloue.accounts.forms import EmailPasswordResetForm, PatronSetPasswordForm
from eloue.accounts.views import activate, authenticate, authenticate_headless, contact, associate_facebook

from eloue.products.views import homepage, search, reply_product_related_message, homepage_object_list
from eloue.products.search_indexes import product_only_search, car_search, realestate_search
from eloue.sitemaps import CategorySitemap, FlatPageSitemap, PatronSitemap, ProductSitemap

from functools import partial

log = logbook.Logger('eloue')

try:
    admin.autodiscover()
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)

sitemaps = {
    'category': CategorySitemap,
    'flatpages': FlatPageSitemap,
    'patrons': PatronSitemap,
    'products': ProductSitemap
}

translation.activate(settings.LANGUAGE_CODE)  # Force language for test and dev

urlpatterns = patterns('',
    url(r'^user_geolocation/$', 'eloue.accounts.views.user_geolocation', name='user_geolocation'),
    url(r'^get_user_location/$', 'eloue.accounts.views.get_user_location', name='get_user_location'),
    url(r"^announcements/", include("announcements.urls")),
    url(r'^sitemap.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+).xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^reset/$', password_reset, {
        'is_admin_site': False,
        'password_reset_form': EmailPasswordResetForm,
        'template_name': 'accounts/password_reset_form.html',
        'email_template_name': 'accounts/password_reset_email'
        }, name="password_reset"),
    url(r'^reset/done/$', password_reset_done, {
        'template_name': 'accounts/password_reset_done.html'
    }, name="password_reset_done"),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
        'set_password_form': PatronSetPasswordForm,
        'template_name': 'accounts/password_reset_confirm.html'
    }, name="password_reset_confirm"),
    url(r'^reset/complete/$', password_reset_complete, {
        'template_name': 'accounts/password_reset_complete.html'
    }, name="password_reset_complete"),
    url(r'^faq/', include('faq.urls')),
    url(r'^contact/$', contact, name="contact"),
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='auth_activate'),
    url(r'^login/$', authenticate, name='auth_login'),
    url(r'^login_headless/$', authenticate_headless, name='auth_login_headless'),
    url(r'^logout/$', logout_then_login, name='auth_logout'),
    url(r'^dashboard/', include('eloue.dashboard.urls')),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^%s' % _("loueur/"), include('eloue.accounts.urls')),
    url(r'^%s' % _("location/"), include('eloue.products.urls')),
    url(r'^booking/', include('eloue.rent.urls')),
    url(r'^experiments/', include('django_lean.experiments.urls')),
    url(r'^edit/reports/', include('django_lean.experiments.admin_urls')),
    url(r'^edit/', include(admin.site.urls)),
    url(r'^edit/stats/', include('eloue.reporting.admin_urls')),
    url(r'^api/', include('eloue.api.urls')),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^$', homepage, name="home"),
    url(r'^lists/object/(?P<offset>[0-9]*)$', partial(homepage_object_list, search_index=product_only_search), name=''),
    url(r'^lists/car/(?P<offset>[0-9]*)$', partial(homepage_object_list, search_index=car_search), name=''),
    url(r'^lists/realestate/(?P<offset>[0-9]*)$', partial(homepage_object_list, search_index=realestate_search), name=''),
    url(r'^%s/$' % _('recherche'), search, name="search"),
    url(r'^propw/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
        'set_password_form': PatronSetPasswordForm,
        'template_name': 'accounts/password_reset_confirm.html',
    }, name="propw"),
)

handler404 = 'eloue.views.custom404'
