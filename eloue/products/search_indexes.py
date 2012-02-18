#-*- coding: utf-8 -*-
import datetime

from django.conf import settings

from haystack.sites import site
from haystack.indexes import CharField, DateTimeField, DateField, FloatField, MultiValueField, EdgeNgramField
from haystack.exceptions import AlreadyRegistered
from haystack.query import SearchQuerySet

from queued_search.indexes import QueuedSearchIndex

from eloue.products.models import Alert, Product
from eloue.rent.models import Booking

__all__ = ['ProductIndex', 'product_search', 'AlertIndex', 'alert_search']


class ProductIndex(QueuedSearchIndex):
    categories = MultiValueField(faceted=True)
    created_at = DateTimeField(model_attr='created_at')
    created_at_date = DateField()
    description = EdgeNgramField(model_attr='description')
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    city = CharField(model_attr='address__city', indexed=False)
    zipcode = CharField(model_attr='address__zipcode', indexed=False)
    owner = CharField(model_attr='owner__username', faceted=True)
    owner_url = CharField(model_attr='owner__get_absolute_url', indexed=False)
    price = FloatField(faceted=True)
    sites = MultiValueField(faceted=True)
    summary = EdgeNgramField(model_attr='summary')
    text = CharField(document=True, use_template=True)
    url = CharField(model_attr='get_absolute_url', indexed=False)
    thumbnail = CharField(indexed=False)
    
    def prepare_sites(self, obj):
        return [site.id for site in obj.sites.all()]
    
    def prepare_categories(self, obj):
        if obj.category:
            categories = [category.slug for category in obj.category.get_ancestors(ascending=False)]
            categories.append(obj.category.slug)
            return categories
    
    def prepare_thumbnail(self, obj):
        if obj.pictures.all():
            picture = obj.pictures.all()[0]
            return picture.thumbnail.url
    
    def prepare_created_at_date(self, obj):
        return obj.created_at.date()

    def prepare_price(self, obj):
        # It doesn't play well with season
        now = datetime.datetime.now()
        unit, amount = Booking.calculate_price(obj, now, now + datetime.timedelta(days=1))
        return amount
    
    def get_queryset(self):
        return Product.on_site.active()
        

class AlertIndex(QueuedSearchIndex):
    designation = CharField(model_attr='designation')
    description = CharField(model_attr='description')
    created_at = DateTimeField(model_attr='created_at')
    patron = CharField(model_attr='patron__username', null=True)
    patron_url = CharField(model_attr='patron__get_absolute_url')
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    text = CharField(document=True, use_template=True)
    sites = MultiValueField(faceted=True)
    url = CharField(model_attr='get_absolute_url', indexed=False)
    
    def prepare_sites(self, obj):
        return [site.id for site in obj.sites.all()]
    
    def get_queryset(self):
        return Alert.on_site.all()
    

try:
    site.register(Product, ProductIndex)
    site.register(Alert, AlertIndex)
except AlreadyRegistered:
    pass


product_search = SearchQuerySet().models(Product).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)
alert_search = SearchQuerySet().models(Alert)

