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

from rest_framework import routers

from accounts.forms import EmailPasswordResetForm, PatronSetPasswordForm
from accounts.views import activate, authenticate, authenticate_headless, contact, google_oauth_callback, patron_subscription
from products.views import homepage, search, reply_product_related_message, homepage_object_list
from products.search import product_only_search, car_search, realestate_search
from sitemaps import CategorySitemap, FlatPageSitemap, PatronSitemap, ProductSitemap

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

from accounts import views as accounts_api
from products import views as products_api
from rent import views as rent_api

class UserMeViewSet(accounts_api.UserViewSet):
    def retrieve_me(self, request, pk=None, *args, **kwargs):
        # use currently authenticated user's ID as pk, ignoring the input argument
        pk = request.user.pk
        self.kwargs[self.pk_url_kwarg] = pk
        return super(UserMeViewSet, self).retrieve(request, pk=pk, *args, **kwargs)

    def update_me(self, request, pk=None, *args, **kwargs):
        # use currently authenticated user's ID as pk, ignoring the input argument
        pk = request.user.pk
        self.kwargs[self.pk_url_kwarg] = pk
        return super(UserMeViewSet, self).update(request, pk=pk, *args, **kwargs)

# See http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#restful
router = routers.DefaultRouter()
router.register(r'users', accounts_api.UserViewSet, base_name='patron')
router.register(r'addresses', accounts_api.AddressViewSet, base_name='address')
router.register(r'phonenumbers', accounts_api.PhoneNumberViewSet, base_name='phonenumber')
router.register(r'proagencies', accounts_api.ProAgencyViewSet, base_name='proagency')
router.register(r'propackages', accounts_api.ProPackageViewSet, base_name='propackage')
router.register(r'subscriptions', accounts_api.SubscriptionViewSet, base_name='subscription')
router.register(r'billings', accounts_api.BillingViewSet, base_name='billing')
router.register(r'billingsubscriptions', accounts_api.BillingSubscriptionViewSet, base_name='billingsubscription')
router.register(r'categories', products_api.CategoryViewSet, base_name='category')
router.register(r'categorydescriptions', products_api.CategoryDescriptionViewSet, base_name='categorydescription')
router.register(r'products', products_api.ProductViewSet, base_name='product')
router.register(r'carproducts', products_api.CarProductViewSet, base_name='carproduct')
router.register(r'realestateproducts', products_api.RealEstateProductViewSet, base_name='realestateproduct')
router.register(r'prices', products_api.PriceViewSet, base_name='price')
router.register(r'pictures', products_api.PictureViewSet, base_name='picture')
router.register(r'curiosities', products_api.CuriosityViewSet, base_name='curiosity')
router.register(r'messagethreads', products_api.MessageThreadViewSet, base_name='messagethread')
router.register(r'productrelatedmessages', products_api.ProductRelatedMessageViewSet, base_name='productrelatedmessage')
router.register(r'bookings', rent_api.BookingViewSet, base_name='booking')
router.register(r'comments', rent_api.CommentViewSet, base_name='comment')
router.register(r'sinisters', rent_api.SinisterViewSet, base_name='sinister')

class ExtraContextTemplateView(TemplateView):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContextTemplateView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

partials_urlpatterns = patterns('',
    url(r'^homepage/login-form.html$', TemplateView.as_view(
        template_name='jade/_log_in.jade',
        ), name='new_ui_homepage_login',
    ),
    url(r'^homepage/registration-form.html$', TemplateView.as_view(
        template_name='jade/_sign_in.jade',
        ), name='new_ui_homepage_registration',
    ),
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

newui_urlpatterns = patterns('',
    url(r'^$', ExtraContextTemplateView.as_view(
        template_name='index.jade',
        extra_context={
            'cities': city_list,
        }),
        name='new_ui_index',
    ),
    url(r'^partials/', include(partials_urlpatterns, namespace='new_ui_partials')),
)

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

    # OAuth2
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')), # django-oauth2-provider
#    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')), # django-oauth-toolkit

    # API 2.0
    url(r'^api/2.0/users/me/$', UserMeViewSet.as_view({'get': 'retrieve_me', 'put': 'update_me'})),
    url(r'^api/2.0/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # UI v3
    url(r'^new_ui/', include(newui_urlpatterns, namespace='ui3')),
    # social: support for sign-in by Google and/or Facebook
#    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
)

handler404 = 'eloue.views.custom404'
