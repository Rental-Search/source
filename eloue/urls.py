# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.utils import translation
from django.views.generic import TemplateView

from sitemaps import CategorySitemap, FlatPageSitemap, PatronSitemap, ProductSitemap

from eloue.api.urls import router
from products.views import HomepageView
from accounts.views import PasswordResetView, PasswordResetConfirmView

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

partials_urlpatterns = patterns('',
    url(r'^homepage/login-form.html$', TemplateView.as_view(
            template_name='jade/_log_in.jade',
        ),
    ),
    url(r'^homepage/registration-form.html$', TemplateView.as_view(
            template_name='jade/_sign_in.jade',
        ),
    ),
    url(r'^homepage/reset-password-form.html$', TemplateView.as_view(
            template_name='jade/_reset_password.jade',
        ),
    ),

    url(r'^publish_item/publish_item.html$', TemplateView.as_view(
            template_name='jade/_pop_up_publish_item.jade',
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
    url(r'^dashboard/items/terms/car_terms.html$', TemplateView.as_view(
            template_name='dashboard/items/terms/car_terms.jade',
        ),
    ),
    url(r'^dashboard/items/terms/professional_terms.html$', TemplateView.as_view(
            template_name='dashboard/items/terms/professional_terms.jade',
        ),
    ),
    url(r'^dashboard/items/terms/simple_terms.html$', TemplateView.as_view(
            template_name='dashboard/items/terms/simple_terms.jade',
        ),
    ),
    url(r'^dashboard/items/terms/real_estate_terms.html$', TemplateView.as_view(
            template_name='dashboard/items/terms/real_estate_terms.jade',
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
    url(r'^dashboard/login.html$', TemplateView.as_view(
            template_name='dashboard/jade/_login.jade',
         ),
    ),
)

dashboard_base_view = TemplateView.as_view(
    template_name='dashboard/jade/_base_dashboard.jade',
)

dashboard_urlpatterns = patterns('',
    url(r'^$', dashboard_base_view, name='dashboard'),
    url(r'^#/messages$', dashboard_base_view, name='messages'),
    url(r'^#/bookings', dashboard_base_view, name='bookings'),
    url(r'^#/items', dashboard_base_view, name='items'),
    url(r'^#/account/profile', dashboard_base_view, name='account'),
    url(r'^partials/', include(partials_urlpatterns, namespace='dashboard_partials')),
)

api2_urlpatterns = patterns('',
    # OAuth2
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')), # django-oauth2-provider
#    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')), # django-oauth-toolkit

    url(r'^api/2.0/', include(router.urls)),
)
if settings.DEBUG:
    api2_urlpatterns += patterns('',
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    )

reset_urlpatterns = patterns('',
    url(r'^$', PasswordResetView.as_view(), {
        'email_template_name': 'accounts/emails/password_reset_email'
    }, name='password_reset'),
    url(r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'
    ),
)

from products.urls import ui3_urlpatterns as products_urlpatterns
from accounts.urls import ui3_urlpatterns as accounts_urlpatterns

ui3_urlpatterns = patterns('',
    url(r'^$', HomepageView.as_view(), name='home'),
    url(r'^loueur/', include(accounts_urlpatterns)),
    url(r'^reset/', include(reset_urlpatterns)),
    url(r'^location/', include(products_urlpatterns)),
    url(r'^comment-ca-marche/', TemplateView.as_view(template_name='how_it_works/index.jade'), name='howto'),
    url(r'^offre-professionnel/', TemplateView.as_view(template_name='subscription/index.jade'), name='subscription'),
    #url(r'^simulez-vos-revenus/', TemplateView.as_view(template_name='simulator/index.jade'), name='simulator'),
    url(r'^dashboard/#/bookings/(?P<pk>[0-9a-f]{32})/$', dashboard_base_view, name='booking_detail'),
    url(r'^dashboard/', include(dashboard_urlpatterns, namespace='dashboard')),
    url(r'^partials/', include(partials_urlpatterns, namespace='partials')),
    url(r'^nos-partenaires/', TemplateView.as_view(template_name='our_partners/index.jade'), name='our_partners'),
    url(r'^contactez-nous/', TemplateView.as_view(template_name='contact_us/index.jade'), name='contact_us'),
    url(r'^espace-presse/', TemplateView.as_view(template_name='press/index.jade'), name='press_page'),
    url(r'^qui-sommes-nous/', TemplateView.as_view(template_name='who_are_we/index.jade'), name='who_are_we'),
    url(r'^securite/', TemplateView.as_view(template_name='security/index.jade'), name='security'),
)

urlpatterns = patterns('',

    url(r'^faq/', include('faq.urls')),

    #url(r'^loueur/', include('accounts.urls')),
    #url(r'^location/', include('products.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # API 2.0
    url(r'^', include(api2_urlpatterns)),

    # UI v3
    url(r'^', include(ui3_urlpatterns)), # namespace='ui3'

    # social: support for sign-in by Google and/or Facebook
#    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
)

handler404 = 'eloue.views.custom404'
