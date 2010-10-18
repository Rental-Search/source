#-*- coding: utf-8 -*-
import datetime

from haystack.sites import site
from haystack.indexes import CharField, DateTimeField, FloatField, MultiValueField
from haystack.exceptions import AlreadyRegistered
from haystack.query import SearchQuerySet

from queued_search.indexes import QueuedSearchIndex

from eloue.products.models import Product
from eloue.rent.models import Booking

__all__ = ['ProductIndex', 'product_search']

class ProductIndex(QueuedSearchIndex):
    categories = MultiValueField(faceted=True)
    created_at = DateTimeField(model_attr='created_at')
    description = CharField(model_attr='description')
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    owner = CharField(model_attr='owner__slug', faceted=True)
    price = FloatField(faceted=True)
    summary = CharField(model_attr='summary')
    text = CharField(document=True, use_template=True)
    
    def prepare_categories(self, obj):
        """
        >>> from eloue.products.models import Category
        >>> parent = Category(slug='parent', parent=None)
        >>> category = Category(slug='child', parent=parent)
        >>> product = Product(category=category)
        >>> ProductIndex(Category).prepare_categories(product)
        ['child', 'parent']
        """
        categories = [ obj.category ]
        def _traverse(category, categories=[]):
            if category.parent:
                categories.append(category.parent)
                _traverse(category.parent, categories)
            return categories
        categories = _traverse(obj.category, categories)
        return [ category.slug for category in categories ]
    
    def prepare_price(self, obj):
        # It doesn't play well with season
        now = datetime.datetime.now()
        return Booking.calculate_price(obj, now, now + datetime.timedelta(days=1))
    
    def get_queryset(self):
        return Product.objects.active()
    

try:
    site.register(Product, ProductIndex)
except AlreadyRegistered:
    pass


product_search = SearchQuerySet().facet('categories').facet('owner').facet('price')
