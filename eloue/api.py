# -*- coding: utf-8 -*-
from tempfile import NamedTemporaryFile
from base64 import decodestring
from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization


from django.conf import settings

from eloue.geocoder import Geocoder
from eloue.products.models import Product, Category, Picture
from eloue.products.search_indexes import product_search
from eloue.accounts.models import Address

__all__ = ['api_v1']

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)

class MetaBase():
    """
    Define meta attributes that must be shared between all resources
    """
    authentication = BasicAuthentication()
    authorization = DjangoAuthorization()


class AddressRessource(ModelResource):
    """
    Ressource that sends back the addresses linked to the user
    """
    class Meta(MetaBase):
        queryset = Address.objects.all()
        resource_name = "address"
        allowed_methods = ['get', 'post']

    def get_list(self, request, **kwargs):
        # Inject the request user in keyword arguments, to get it in obj_get_list
        return ModelResource.get_list(self, request, user=request.user, **kwargs)

    def obj_get_list(self, filters=None, user=None, **kwargs):
        # Get back the user object injected in get_list, and add it to the filters
        mfilters = dict(filters)
        mfilters["user"] = user
        return ModelResource.obj_get_list(self, mfilters, **kwargs)

    def build_filters(self, filters):
        # Filter on user
        return {'patron': filters["user"]}

class CategoryRessource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']
        fields = ['id', 'name', 'slug']


class ProductRessource(ModelResource):
    category = fields.ForeignKey(CategoryRessource, 'category', full=True)

    class Meta(MetaBase):
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

        if "l" in filters:
            lat, lon = Geocoder.geocode(filters['l'])
            radius = filters.get('r', DEFAULT_RADIUS)
            if lat and lon:
                sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')

        orm_filters = {"pk__in": [i.pk for i in sqs]}
        return orm_filters

    def is_authorized(self, request, object=None):
        ModelResource.is_authorized(self, request, object)
        print "INTO is_authorized"
        print "USER : ", request.user, type(request.user)

    def obj_create(self, bundle):
        data = bundle.data
        new_product = bundle.obj

        # Create the picture object if there is a picture in the request
        if data.get("picture", None):
            tmp_img = NamedTemporaryFile("w")
            tmp_img.write(decodestring(data["picture"]))
            picture = Picture.objects.create(image=tmp_img)

        # address = 




api_v1 = Api(api_name='1.0')
api_v1.register(CategoryRessource())
api_v1.register(ProductRessource())
api_v1.register(AddressRessource())
