#-*- coding: utf-8 -*-
from haystack.sites import site
from haystack.indexes import RealTimeSearchIndex, CharField, BooleanField, IntegerField, DateField, FloatField, MultiValueField
from haystack.exceptions import AlreadyRegistered

from eloue.products.models import Product

class ProductIndex(RealTimeSearchIndex):
    summary = CharField(model_attr='summary')
    categories = MultiValueField()
    owner = CharField(model_attr='owner__slug')
    text = CharField(document=True, use_template=True)
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    
    def prepare_categories(self, obj):
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
