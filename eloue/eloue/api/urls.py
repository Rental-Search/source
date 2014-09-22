from django.conf import settings
from django.conf.urls import patterns, url, include

from rest_framework import routers

from eloue.api.resources import api_v1
from eloue.api import views

urlpatterns = patterns('',
    url(r'^1.0/update_product_prices/$', views.update_product_prices, name='update_product_prices'),
    url(r'^', include(api_v1.urls)),
)

from accounts import views as accounts_api
from products import views as products_api
from rent import views as rent_api

# See http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#restful
router = routers.DefaultRouter()
router.register(r'users', accounts_api.UserViewSet, base_name='patron')
router.register(r'addresses', accounts_api.AddressViewSet, base_name='address')
router.register(r'phones', accounts_api.PhoneNumberViewSet, base_name='phonenumber')
router.register(r'credit_cards', accounts_api.CreditCardViewSet, base_name='creditcard')
router.register(r'pro_agencies', accounts_api.ProAgencyViewSet, base_name='proagency')
router.register(r'pro_packages', accounts_api.ProPackageViewSet, base_name='propackage')
router.register(r'subscriptions', accounts_api.SubscriptionViewSet, base_name='subscription')
router.register(r'billings', accounts_api.BillingViewSet, base_name='billing')
router.register(r'billing_subscriptions', accounts_api.BillingSubscriptionViewSet, base_name='billingsubscription')
router.register(r'categories', products_api.CategoryViewSet, base_name='category')
router.register(r'products', products_api.ProductViewSet, base_name='product')
router.register(r'prices', products_api.PriceViewSet, base_name='price')
router.register(r'pictures', products_api.PictureViewSet, base_name='picture')
router.register(r'curiosities', products_api.CuriosityViewSet, base_name='curiosity')
router.register(r'messagethreads', products_api.MessageThreadViewSet, base_name='messagethread')
router.register(r'productrelatedmessages', products_api.ProductRelatedMessageViewSet, base_name='productrelatedmessage')
router.register(r'bookings', rent_api.BookingViewSet, base_name='booking')
router.register(r'comments', rent_api.CommentViewSet, base_name='comment')
router.register(r'sinisters', rent_api.SinisterViewSet, base_name='sinister')
