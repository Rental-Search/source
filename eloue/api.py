# -*- coding: utf-8 -*-
import os

from base64 import decodestring

from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.utils import dict_strip_unicode_keys
from tastypie.http import HttpCreated

from django.conf import settings

from eloue.geocoder import GoogleGeocoder
from eloue.products.models import Product, Category, Picture, Price, upload_to
from eloue.products.search_indexes import product_search
from eloue.accounts.models import Address, PhoneNumber, Patron
from eloue.rent.models import Booking

__all__ = ['api_v1']

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class MetaBase():
    """Define meta attributes that must be shared between all resources"""
    authentication = BasicAuthentication()
    authorization = DjangoAuthorization()


class UserSpecificResource(ModelResource):
    """
    Base class for a resource that restrain the possible actions to the scope of the user
    For GET: Only user owned objects are returned
    For POST: The objects created are automatically owned by the user
    """
    # TODO : Make it work the same way with obj_get than with get_list
    USER_FIELD_NAME = "patron"
    
    def get_list(self, request, **kwargs):
        # Inject the request user in keyword arguments, to get it in obj_get_list
        return ModelResource.get_list(self, request, user=request.user, **kwargs)
    
    def obj_get_list(self, filters=None, user=None, **kwargs):
        # Get back the user object injected in get_list, and add it to the filters
        # If FILTER_GET_REQUESTS is true
        mfilters = dict(filters)
        mfilters["user"] = user
        return ModelResource.obj_get_list(self, mfilters, **kwargs)
    
    def build_filters(self, filters):
        # Filter on user
        f = {}
        f[self.USER_FIELD_NAME] = filters["user"]
        return f
    
    def post_list(self, request, **kwargs):
        """
        Copy of the tastypie post_list implementation
        Necessary to send the user to obj_create
        """
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized))
        # Add the user to the fields to be added
        kwargs[self.USER_FIELD_NAME] = request.user
        updated_bundle = self.obj_create(bundle, **kwargs)
        return HttpCreated(location=self.get_resource_uri(updated_bundle))
    

class PhoneNumberResource(UserSpecificResource):
    """Resource that sends back the phone numbers linked to the user"""
    class Meta(MetaBase):
        queryset = PhoneNumber.objects.all()
        resource_name = "phonenumber"
        allowed_methods = ['get', 'post']
    

class AddressResource(UserSpecificResource):
    """Resource that sends back the addresses linked to the user"""
    class Meta(MetaBase):
        queryset = Address.objects.all()
        resource_name = "address"
        allowed_methods = ['get', 'post']
    

class CategoryResource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']
        fields = ['id', 'name', 'slug']
    

class PictureResource(ModelResource):    
    class Meta:
        queryset = Picture.objects.all()
        resource_name = 'picture'
        allowed_methods = ['get']
        fields = ['id']
    
    def dehydrate(self, bundle, request=None):
        bundle.data['thumbnail_url'] = bundle.obj.thumbnail.url
        bundle.data['display_url'] = bundle.obj.display.url
        return bundle
    

class ProductResource(UserSpecificResource):
    category = fields.ForeignKey(CategoryResource, 'category', full=True, null=True)
    address = fields.ForeignKey(AddressResource, 'address', full=True, null=True)
    pictures = fields.ToManyField(PictureResource, 'pictures', full=True)
    
    USER_FIELD_NAME = "owner"
    
    def dispatch(self, request_type, request, **kwargs):
        # Ugly hack around django WSGIRequest bug ...
        # When sending big requests (containing a picture for example), the basic auth header is disappearing
        # Unless we call __repr__ on the request
        # TODO: This really needs further investigation
        request.__repr__()
        return UserSpecificResource.dispatch(self, request_type, request, **kwargs)
    
    class Meta(MetaBase):
        queryset = Product.objects.all()
        allowed_methods = ['get', 'post']
        resource_name = 'product'
        fields = ['id', 'quantity', 'summary', 'description', 'deposit_amount']
        filtering = {
            'category': ALL_WITH_RELATIONS,
            'owner': ALL_WITH_RELATIONS
        }
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(UserSpecificResource, self).build_filters(filters)
        sqs = product_search
        if "q" in filters:
            sqs = sqs.auto_query(filters['q'])
        
        if "l" in filters:
            name, (lat, lon) = GoogleGeocoder().geocode(filters['l'])
            radius = filters.get('r', DEFAULT_RADIUS)
            if lat and lon:
                sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
        
        orm_filters = {"pk__in": [i.pk for i in sqs]}
        return orm_filters
    
    def obj_create(self, bundle, **kwargs):
        """
        On product creation, if the request contains a "picture" parameter
        Creates a file with the content of the field
        And creates a picture linked to the product
        """
        picture_data = bundle.data.get("picture", None)
        if picture_data:
            bundle.data.pop("picture")
        updated_bundle = UserSpecificResource.obj_create(self, bundle, **kwargs)
        
        # Create the picture object if there is a picture in the request
        if picture_data:
            picture = Picture(product=updated_bundle.obj)
            # Write the image content to a file
            img_path = upload_to(picture, "")
            img = file(os.path.join(settings.MEDIA_ROOT, img_path), "w")
            img.write(decodestring(picture_data))
            img.close()
            picture.image.name = img_path
            picture.save()
        return updated_bundle
    
    def dehydrate(self, bundle, request=None):
        """
        Automatically add the location price if the request
        contains date_start and date_end parameters
        """
        from datetime import datetime, timedelta
        from dateutil import parser
        
        if "date_start" in request.GET and "date_end" in request.GET:
            date_start = parser.parse(request.GET["date_start"])
            date_end = parser.parse(request.GET["date_end"])
        else:
            date_start = datetime.now() + timedelta(days=1)
            date_end = date_start + timedelta(days=1)
        bundle.data["price"] = Booking.calculate_price(bundle.obj, date_start, date_end)
        return bundle
    

class PriceResource(ModelResource):
    product = fields.ForeignKey(ProductResource, 'product', full=False)
    
    class Meta(MetaBase):
        queryset = Price.objects.all()
        resource_name = "price"
        fields = []
        allowed_methods = ['get', 'post']
    

class UserResource(ModelResource):  # TODO : Add security checks for user creation
    class Meta(MetaBase):
        queryset = Patron.objects.all()
        resource_name = "user"
        allowed_methods = ['get', 'post']
        fields = ['username', 'id']
    
    def obj_create(self, bundle, **kwargs):
        """Creates a new inactive user"""
        data = bundle.data
        bundle.obj = Patron.objects.create_inactive(data["username"], data["email"], data["password"])
        return bundle
    

api_v1 = Api(api_name='1.0')
api_v1.register(CategoryResource())
api_v1.register(ProductResource())
api_v1.register(AddressResource())
api_v1.register(PhoneNumberResource())
api_v1.register(PictureResource())
api_v1.register(PriceResource())
api_v1.register(UserResource())
