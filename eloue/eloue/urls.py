# -*- coding: utf-8 -*-
import logbook
from functools import partial

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.auth.views import logout_then_login, password_reset, password_reset_confirm, password_reset_confirm_uidb36, password_reset_done, password_reset_complete
from django.contrib.sitemaps.views import index, sitemap
from django.utils import translation
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from accounts.forms import EmailPasswordResetForm, PatronSetPasswordForm
from accounts.views import activate, authenticate, authenticate_headless, contact, google_oauth_callback, patron_subscription
from products.views import homepage, search, reply_product_related_message, homepage_object_list
from products.search import product_only_search, car_search, realestate_search
from sitemaps import CategorySitemap, FlatPageSitemap, PatronSitemap, ProductSitemap
from eloue.api.urls import router, UserMeViewSet

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
    url(r'^invitation_sent/$', TemplateView.as_view(template_name='accounts/invitation_sent.html'), name='invitation_sent'),
    url(r'^user_geolocation/$', 'accounts.views.user_geolocation', name='user_geolocation'),
    url(r'^get_user_location/$', 'accounts.views.get_user_location', name='get_user_location'),
    url(r"^announcements/", include("announcements.urls")),
    url(r'^sitemap.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+).xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^reset/$', password_reset, {
        'is_admin_site': False,
        'password_reset_form': EmailPasswordResetForm,
        'template_name': 'accounts/password_reset_form.html',
        'email_template_name': 'accounts/emails/password_reset_email'
        }, name="password_reset"),
    url(r'^reset/done/$', password_reset_done, {
        'template_name': 'accounts/password_reset_done.html'
    }, name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, {
        'set_password_form': PatronSetPasswordForm,
        'template_name': 'accounts/password_reset_confirm.html'
    }, name="password_reset_confirm"),
    # TODO: You can remove this url pattern after your app has been deployed with Django 1.6 for PASSWORD_RESET_TIMEOUT_DAYS (3 days).
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm_uidb36, {
        'set_password_form': PatronSetPasswordForm,
        'template_name': 'accounts/password_reset_confirm.html'
    }),
    url(r'^reset/complete/$', password_reset_complete, {
        'template_name': 'accounts/password_reset_complete.html'
    }, name="password_reset_complete"),
    url(r'^espace_pro/$', patron_subscription, name="patron_subscription"),
    url(r'^faq/', include('faq.urls')),
    url(r'^contact/$', contact, name="contact"),
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='auth_activate'),
    url(r'^login/$', authenticate, name='auth_login'),
    url(r'^login_headless/$', authenticate_headless, name='auth_login_headless'),
    url(r'^logout/$', logout_then_login, name='auth_logout'),
    url(r'^oauth2callback$', google_oauth_callback),
    url(r'^dashboard/', include('eloue.dashboard.urls')),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^%s' % "loueur/", include('accounts.urls')),
    url(r'^%s' % "location/", include('products.urls')),
    url(r'^%s' % "jeu-concours/", include('contest.urls')),
    url(r'^booking/', include('rent.urls')),
    url(r'^experiments/', include('django_lean.experiments.urls')),
    url(r'^edit/reports/', include('django_lean.experiments.admin_urls')),
    url(r'^edit/', include(admin.site.urls)),
    url(r'edit/', include('accounts.admin_urls')),
    url(r'^edit/stats/', include('reporting.admin_urls')),
    url(r'^api/', include('eloue.api.urls')),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^slimpay/', include('payments.slimpay_urls')),
    url(r'^$', homepage, name="home"),
    url(r'^lists/object/(?P<offset>[0-9]*)$', partial(homepage_object_list, search_index=product_only_search), name=''),
    url(r'^lists/car/(?P<offset>[0-9]*)$', partial(homepage_object_list, search_index=car_search), name=''),
    url(r'^lists/realestate/(?P<offset>[0-9]*)$', partial(homepage_object_list, search_index=realestate_search), name=''),
    url(r'^%s/$' % 'recherche', search, name="search"),
    url(r'^propw/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, {
        'set_password_form': PatronSetPasswordForm,
        'template_name': 'accounts/professional_password_reset_confirm.html',
    }, name="propw"),
    # TODO: You can remove this url pattern after your app has been deployed with Django 1.6 for PASSWORD_RESET_TIMEOUT_DAYS (3 days).
    url(r'^propw/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm_uidb36, {
        'set_password_form': PatronSetPasswordForm,
        'template_name': 'accounts/professional_password_reset_confirm.html',
    }),
)


class ExtraContextTemplateView(TemplateView):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContextTemplateView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

partials_urlpatterns = patterns('',
    url(r'^homepage/login-form.html$', TemplateView.as_view(
            template_name='jade/_log_in.jade',
        ),
    ),
    url(r'^homepage/registration-form.html$', TemplateView.as_view(
            template_name='jade/_sign_in.jade',
        ),
    ),

    url(r'^dashboard/dashboard.html$', TemplateView.as_view(
            template_name='dashboard/dashboard/index.jade',
        ),
    ),
    url(r'^dashboard/messages.html$', TemplateView.as_view(
            template_name='dashboard/messages/index.jade',
        ),
    ),
    url(r'^dashboard/bookings.html$', TemplateView.as_view(
            template_name='dashboard/booking/index.jade',
        ),
    ),
    url(r'^dashboard/items.html$', TemplateView.as_view(
            template_name='dashboard/items/_base_items.jade',
        ),
    ),
    url(r'^dashboard/account.html$', TemplateView.as_view(
            template_name='dashboard/account/_base_account.jade',
        ),
    ),

    url(r'^dashboard/messages/message_detail.html$', TemplateView.as_view(
            template_name='dashboard/messages/message_detail.jade',
        ),
    ),

    url(r'^dashboard/bookings/booking_detail.html$', TemplateView.as_view(
            template_name='dashboard/booking/_bookings_detaild.jade',
        ),
    ),

    url(r'^dashboard/items/item_detail.html$', TemplateView.as_view(
            template_name='dashboard/items/item_detail.jade',
        ),
    ),
    url(r'^dashboard/items/tabs.html$', TemplateView.as_view(
            template_name='dashboard/items/tabs.jade',
        ),
    ),
    url(r'^dashboard/items/info.html$', TemplateView.as_view(
            template_name='dashboard/items/index.jade',
        ),
    ),
    url(r'^dashboard/items/tariffs.html$', TemplateView.as_view(
            template_name='dashboard/items/tarifs.jade',
        ),
    ),
    url(r'^dashboard/items/calendar.html$', TemplateView.as_view(
            template_name='dashboard/items/calendar.jade',
        ),
    ),
    url(r'^dashboard/items/terms.html$', TemplateView.as_view(
            template_name='dashboard/items/terms.jade',
        ),
    ),
    url(r'^dashboard/items/profits.html$', TemplateView.as_view(
            template_name='dashboard/items/profits.jade',
        ),
    ),

    url(r'^dashboard/account/profile.html$', TemplateView.as_view(
            template_name='dashboard/account/profil.jade',
        ),
    ),
    url(r'^dashboard/account/verification.html$', TemplateView.as_view(
            template_name='dashboard/account/verification.jade',
        ),
    ),
    url(r'^dashboard/account/addresses.html$', TemplateView.as_view(
            template_name='dashboard/account/address.jade',
        ),
    ),
    url(r'^dashboard/account/phones.html$', TemplateView.as_view(
            template_name='dashboard/account/phones.jade',
        ),
    ),
    url(r'^dashboard/account/payments.html$', TemplateView.as_view(
            template_name='dashboard/account/payments.jade',
        ),
    ),
    url(r'^dashboard/account/password.html$', TemplateView.as_view(
            template_name='dashboard/account/password.jade',
        ),
    ),
    url(r'^dashboard/account/invitation.html$', TemplateView.as_view(
            template_name='dashboard/account/invitation.jade',
        ),
    ),
    url(r'^dashboard/account/address_detail.html$', TemplateView.as_view(
            template_name='dashboard/account/_address_detail.jade',
        ),
    ),
)

dashboard_urlpatterns = patterns('',
    url(r'^$', ExtraContextTemplateView.as_view(
            template_name='dashboard/jade/_base_dashboard.jade',
        ),
        name='new_ui_dashboard',
    ),
    url(r'^partials/', include(partials_urlpatterns, namespace='new_ui_dashboard_partials')),
)

city_list = [
    {"name": "paris", "actives": 123254},
    {"name": "lyon", "actives": 98453},
    {"name": "toulouse", "actives": 90657},
    {"name": "nantes", "actives": 123254},
    {"name": "rennes", "actives": 98453},
    {"name": "bordeaux", "actives": 90657},
    {"name": "lille", "actives": 123254},
    {"name": "montpelier", "actives": 98453},
    {"name": "rouen", "actives": 90657},
]

urlpatterns = patterns('',
    # OAuth2
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')), # django-oauth2-provider
#    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')), # django-oauth-toolkit

    # API 2.0
    url(r'^api/2.0/users/me/', UserMeViewSet.as_view({'get': 'retrieve_me', 'put': 'update_me'})),
    url(r'^api/2.0/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^admin/', include(admin.site.urls)),

    # UI v3
    url(r'^$', ExtraContextTemplateView.as_view(
            template_name='index.jade',
            extra_context={
                'cities': city_list,
            }
        ),
        name='new_ui_homepage',
    ),
    url(r'^lists/', ExtraContextTemplateView.as_view(
            template_name='products/product_list.jade',
        ),
        name='new_ui_product_list',
    ),
    url(r'^dashboard/', include(dashboard_urlpatterns, namespace='new_ui_dashboard')),
    url(r'^partials/', include(partials_urlpatterns, namespace='new_ui_partials')),

    # social: support for sign-in by Google and/or Facebook
#    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
)

handler404 = 'eloue.views.custom404'
