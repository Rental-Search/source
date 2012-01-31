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
from eloue.accounts.views import activate, authenticate, authenticate_headless, dashboard, patron_edit, owner_booking, owner_history,\
    borrower_booking, borrower_history, patron_edit_password, patron_paypal, owner_product, contact, alert_edit, associate_facebook

from eloue.products.views import homepage, search, reply_product_related_message, inbox, archived, archive_thread, unarchive_thread, thread_details

from eloue.rent.views import booking_detail, booking_accept, booking_reject, booking_incident, booking_close, booking_cancel, offer_reject, offer_accept
from eloue.sitemaps import CategorySitemap, FlatPageSitemap, PatronSitemap, ProductSitemap

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
    url(r"^announcements/", include("announcements.urls")),
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
    url(r'^dashboard/$', dashboard, name="dashboard"),
    url(r'^dashboard/account/profile/$', patron_edit, name="patron_edit"),
    url(r'^dashboard/account/password/$', patron_edit_password, name="patron_edit_password"),
    url(r'^dashboard/account/paypal/$', patron_paypal, name="patron_paypal"),
    url(r'^dashboard/account/phonenumbers/$', 'eloue.accounts.views.patron_edit_phonenumber', name="patron_edit_phonenumber"),
    url(r'^dashboard/account/addresses/$', 'eloue.accounts.views.patron_edit_addresses', name="patron_edit_addresses"),
    url(r'^dashboard/account/profile/accounts_work_autocomplete$', 'eloue.accounts.views.accounts_work_autocomplete', name='accounts_work_autocomplete'),
    url(r'^dashboard/account/profile/accounts_studies_autocomplete$', 'eloue.accounts.views.accounts_studies_autocomplete', name='accounts_studies_autocomplete'),
    url(r'^dashboard/owner/booking/$', owner_booking, name="owner_booking"),
    url(r'^dashboard/owner/booking/page/(?P<page>\d+)/$', owner_booking, name="owner_booking"),
    url(r'^dashboard/owner/history/$', owner_history, name="owner_history"),
    url(r'^dashboard/owner/history/page/(?P<page>\d+)/$', owner_history, name="owner_history"),
    url(r'^dashboard/owner/product/$', owner_product, name="owner_product"),
    url(r'^dashboard/alertes/$', alert_edit, name="alert_edit"),
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
    #url(r'^dashboard/messages/(?P<message_id>[\d]+)/reply/$', reply_product_related_message, name='reply_product_related_message'),
    url(r'^dashboard/messages/(?P<thread_id>[\d]+)$', thread_details, name='thread_details'),
    url(r'^dashboard/messages/(?P<thread_id>[\d]+)/archive/$', archive_thread, name='archive_thread'),
    url(r'^dashboard/messages/(?P<thread_id>[\d]+)/unarchive/$', unarchive_thread, name='unarchive_thread'),
    url(r'^dashboard/messages/accept/(?P<booking_id>[0-9a-f]{32})', offer_accept, name='offer_accept'),
    url(r'^dashboard/messages/reject/(?P<booking_id>[0-9a-f]{32})', offer_reject, name='offer_reject'),
    url(r'^dashboard/messages/inbox', inbox, name='inbox'),
    url(r'^dashboard/messages/archived', archived, name='archived'),
    url(r'^dashboard/messages/', include('django_messages.urls')),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^%s' % _("loueur/"), include('eloue.accounts.urls')),
    url(r'^%s' % _("location/"), include('eloue.products.urls')),
    url(r'^booking/', include('eloue.rent.urls')),
    url(r'^experiments/', include('django_lean.experiments.urls')),
    url(r'^edit/reports/', include('django_lean.experiments.admin_urls')),
    url(r'^edit/', include(admin.site.urls)),
    url(r'^api/', include('eloue.api.urls')),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^$', homepage, name="home"),
    url(r'^%s/$' % _('recherche'), search, name="search")
)

handler404 = 'eloue.views.custom404'
