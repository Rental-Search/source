#-*- coding: utf-8 -*-
from haystack.sites import site
from haystack.indexes import RealTimeSearchIndex, CharField, BooleanField, IntegerField, DateField, FloatField
from haystack.exceptions import AlreadyRegistered

from eloue.products.models import Product

class ProductIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    category = CharField(model_attr='category__slug')
    owner = CharField(model_attr='owner__username')
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    
    def get_queryset(self):
        return Product.objects.active()
    
try:
    site.register(Product, ProductIndex)
except AlreadyRegistered:
    pass
