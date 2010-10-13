#-*- coding: utf-8 -*-
from haystack.sites import site
from haystack.indexes import RealTimeSearchIndex, CharField, FloatField, MultiValueField
from haystack.exceptions import AlreadyRegistered
from haystack.query import SearchQuerySet

from eloue.products.models import Product

__all__ = ['ProductIndex', 'product_search']

class ProductIndex(RealTimeSearchIndex):
    summary = CharField(model_attr='summary')
    description = CharField(model_attr='description')
    categories = MultiValueField(faceted=True)
    owner = CharField(model_attr='owner__slug', faceted=True)
    text = CharField(document=True, use_template=True)
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    
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
    
    def get_queryset(self):
        return Product.objects.active()
    

try:
    site.register(Product, ProductIndex)
except AlreadyRegistered:
    pass


product_search = SearchQuerySet().facet('categories').facet('owner')
