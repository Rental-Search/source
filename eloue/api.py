# -*- coding: utf-8 -*-
from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from django.conf import settings

from eloue.geocoder import Geocoder
from eloue.products.models import Product, Category
from eloue.products.search_indexes import product_search

__all__ = ['api_v1']

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class CategoryRessource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']
        fields = ['id', 'name', 'slug']


class ProductRessource(ModelResource):
    category = fields.ForeignKey(CategoryRessource, 'category', full=True)
    
    class Meta:
        queryset = Product.objects.all()
        allowed_methods = ['get', 'post']
        resource_name = 'product'
        fields = ['summary', 'description', 'deposit_amount', 'resource_uri']
        filtering = {
            'category': ALL_WITH_RELATIONS,
        }
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(ProductRessource, self).build_filters(filters)
        sqs = product_search
        if "q" in filters:
            sqs = sqs.auto_query(filters['q'])
        
        if "where" in filters:
            lat, lon = Geocoder.geocode(filters['where'])
            radius = filters.get('radius', DEFAULT_RADIUS)
            if lat and lon:
                sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
        
        orm_filters = {"pk__in": [i.pk for i in sqs]}
        return orm_filters
    

api_v1 = Api(api_name='1.0')
api_v1.register(CategoryRessource())
api_v1.register(ProductRessource())
