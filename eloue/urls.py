# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext as _
from django.contrib import admin
from django.utils import translation
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import index, sitemap

from sitemaps import CategorySitemap, FlatPageSitemap, PatronSitemap, ProductSitemap

from eloue.api.urls import router

from products.views import HomepageView, PublishItemView
from accounts.views import PasswordResetView, PasswordResetConfirmView, ActivationView, LoginAndRedirectView, LoginFacebookView, SignUpLandingView, ContactView

admin.autodiscover()

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
    url(r'^dashboard/items/shipping.html$', TemplateView.as_view(
            template_name='dashboard/items/shipping.jade',
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

from products.urls import urlpatterns as products_urlpatterns
from accounts.urls import urlpatterns as accounts_urlpatterns

urlpatterns = patterns('',
    url(r'^$', HomepageView.as_view(), name='home'),
    url(r'^redirect/', LoginAndRedirectView.as_view(), name='redirect'),
    url(r'^login_facebook/', LoginFacebookView.as_view(), name='login_facebook'),
    url(r'^%s/' % _('loueur'), include(accounts_urlpatterns)),
    url(r'^reset/', include(reset_urlpatterns)),
    url(r'^%s/' % _('location'), include(products_urlpatterns)),
    url(r'^%s/' % _('comment-ca-marche'), TemplateView.as_view(template_name='how_it_works/index.jade'), name='howto'),
    url(r'^%s/' % _('offre-professionnel'), TemplateView.as_view(template_name='subscription/index.jade'), name='subscription'),
    #url(r'^simulez-vos-revenus/', TemplateView.as_view(template_name='simulator/index.jade'), name='simulator'),
    url(r'^dashboard/#/bookings/(?P<pk>[0-9a-f]{32})/$', dashboard_base_view, name='booking_detail'),
    url(r'^dashboard/#/messages/(?P<pk>[0-9]+)/$', dashboard_base_view, name='messages'),
    url(r'^dashboard/', include(dashboard_urlpatterns, namespace='dashboard')),
    url(r'^partials/', include(partials_urlpatterns, namespace='partials')),
    url(r'^%s/' % _('nos-partenaires'), TemplateView.as_view(template_name='our_partners/index.jade'), name='our_partners'),
    url(r'^%s/' % _('contact_nous'), ContactView.as_view() , name='contact_us'),
    #url(r'^espace-presse/', TemplateView.as_view(template_name='press/index.jade'), name='press_page'),
    url(r'^%s/' % _('qui-sommes-nous'), TemplateView.as_view(template_name='who_are_we/index.jade'), name='who_are_we'),
    url(r'^%s/' % _('securite'), TemplateView.as_view(template_name='security/index.jade'), name='security'),
    url(r'^%s/' % _('conditions-generales-particuliers'), TemplateView.as_view(template_name='terms/index.jade'), name='terms'),
    url(r'^%s/' % _('conditions-generales-professionnels'), TemplateView.as_view(template_name='terms_pro/index.jade'), name='terms'),
    url(r'^%s/' % _('contrat-de-location'), TemplateView.as_view(template_name='rental_agreement/index.jade'), name='agreement'),
    # url(r'^depot-de-garantie/', TemplateView.as_view(template_name='deposit_amount/index.jade'), name='agreement'),
    url(r'^%s/' % _('mentions-legales'), TemplateView.as_view(template_name='imprint/index.jade'), name='notices'),
    # url(r'^politique_annulation/', TemplateView.as_view(template_name='cancel_terms/index.jade'), name='notices'),
    url(r'^%s/' % _('assurance-tranquillite'), TemplateView.as_view(template_name='insurances/index.jade'), name='notices'),
    url(r'^%s/' % _('nous-recrutons'), TemplateView.as_view(template_name='enroll/index.jade'), name='enroll'),
    url(r'^activate/(?P<activation_key>\w+)/$', ActivationView.as_view(), name='auth_activate'),
    url(r'^sitemap.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+).xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^navette/', TemplateView.as_view(template_name='shipping/index.jade'), name='shuttle'),
    url(r'^edit/', include(admin.site.urls)),
    url(r'edit/', include('accounts.admin_urls')),
    url(r'^edit/stats/', include('reporting.admin_urls')),
    url(r'^slimpay/', include('payments.slimpay_urls')),
    url(r'^inscription/(?P<campagn_name>\w+)/$', SignUpLandingView.as_view(), name='signup'),

    # API 2.0
    url(r'^', include(api2_urlpatterns)),

    # social: support for sign-in by Google and/or Facebook
#    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:

    from django.conf.urls.static import static
    urlpatterns += patterns('',
        url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#handler404 = 'eloue.views.custom404'