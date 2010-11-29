# -*- coding: utf-8 -*-
from urllib import unquote
from base64 import decodestring

from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.authentication import Authentication
from tastypie.authorization import DjangoAuthorization
from tastypie.http import HttpCreated
from tastypie.utils import dict_strip_unicode_keys
from tastypie.serializers import Serializer

from oauth_provider.decorators import CheckOAuth
from oauth_provider.store import store, InvalidTokenError
from oauth_provider.utils import get_oauth_request
from oauth2 import Error

from django.conf import settings

from eloue.geocoder import GoogleGeocoder
from eloue.products.models import Product, Category, Picture, Price, upload_to
from eloue.products.search_indexes import product_search
from eloue.accounts.models import Address, PhoneNumber, Patron
from eloue.rent.models import Booking

__all__ = ['api_v1']

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class OAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if CheckOAuth.is_valid_request(request):
            oauth_request = get_oauth_request(request)
            consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
            try:
                token = store.get_access_token(request, oauth_request, consumer, oauth_request.get_parameter('oauth_token'))
            except InvalidTokenError:
                return False
            
            try:
                parameters = CheckOAuth.validate_token(request, consumer, token)
            except Error, e:
                return False
            
            if consumer and token:
                request.user = token.user
                return True
        return False
    

class JSONSerializer(Serializer):
    formats = ['json', 'jsonp']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
    }


class MetaBase():
    """Define meta attributes that must be shared between all resources"""
    authentication = OAuthentication()
    authorization = DjangoAuthorization()
    serializer = JSONSerializer()


class OAuthResource(ModelResource):
    def obj_get_list(self, filters=None, user=None, **kwargs):
        """
        Removes every oauth related key
        There is probably a better way but i can't find it
        """
        mfilters = {}
        for key, val in filters.items():
            if not key.startswith("oauth_"):
                mfilters[key] = val
        return super(OAuthResource, self).obj_get_list(mfilters, **kwargs)
    

class UserSpecificResource(OAuthResource):
    """
    Base class for a resource that restrain the possible actions to the scope of the user
    For GET: Only user owned objects are returned
    For POST: The objects created are automatically owned by the user
    """
    # TODO : Make it work the same way with obj_get than with get_list
    USER_FIELD_NAME = "patron"
    FILTER_GET_REQUESTS = True
    
    def get_list(self, request, **kwargs):
        # Inject the request user in keyword arguments, to get it in obj_get_list
        return OAuthResource.get_list(self, request, user=request.user, **kwargs)
    
    def obj_get_list(self, filters=None, user=None, **kwargs):
        # Get back the user object injected in get_list, and add it to the filters
        # If FILTER_GET_REQUESTS is true
        mfilters = {}
        for key, val in filters.items():
            mfilters[key] = val
        
        if self.FILTER_GET_REQUESTS:
            mfilters["user"] = user
        
        return OAuthResource.obj_get_list(self, mfilters, **kwargs)
    
    def build_filters(self, filters):
        # Filter on user
        orm_filters = {}
        user = filters.pop("user") if "user" in filters else None
        orm_filters.update(super(UserSpecificResource, self).build_filters(filters))
        
        if not self.FILTER_GET_REQUESTS:
            return filters
        
        if user:
            orm_filters[self.USER_FIELD_NAME] = user
        
        return orm_filters
    
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
    
    def dehydrate(self, bundle, request=None):
        if bundle.obj.position:
            bundle.data["position"] = {'lat': bundle.obj.position.x, 'lng': bundle.obj.position.y}
        return bundle
    

class CategoryResource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']
        fields = ['id', 'name', 'slug']
    

class PictureResource(OAuthResource):
    class Meta:
        queryset = Picture.objects.all()
        resource_name = 'picture'
        allowed_methods = ['get']
        fields = ['id']
    
    def dehydrate(self, bundle, request=None):
        bundle.data['thumbnail_url'] = bundle.obj.thumbnail.url
        bundle.data['display_url'] = bundle.obj.display.url
        return bundle
    

class UserResource(OAuthResource):  # TODO : Add security checks for user creation
    class Meta(MetaBase):
        queryset = Patron.objects.all()
        resource_name = "user"
        allowed_methods = ['get', 'post']
        fields = ['username', 'id']
        filtering = {
            'username': ALL_WITH_RELATIONS,
        }

    def obj_create(self, bundle, **kwargs):
        """Creates a new inactive user"""
        data = bundle.data
        bundle.obj = Patron.objects.create_inactive(data["username"], data["email"], data["password"])
        return bundle
    

class PriceResource(OAuthResource):
    class Meta(MetaBase):
        queryset = Price.objects.all()
        resource_name = "price"
        fields = []
        allowed_methods = ['get', 'post']
    

class ProductResource(UserSpecificResource):
    category = fields.ForeignKey(CategoryResource, 'category', full=True, null=True)
    address = fields.ForeignKey(AddressResource, 'address', full=True, null=True)
    owner = fields.ForeignKey(UserResource, 'owner', full=False, null=True)
    pictures = fields.ToManyField(PictureResource, 'pictures', full=True, null=True)
    prices = fields.ToManyField(PriceResource, 'prices', full=True, null=True)

    USER_FIELD_NAME = "owner"
    FILTER_GET_REQUESTS = False
    
    class Meta(MetaBase):
        queryset = Product.objects.all()
        allowed_methods = ['get', 'post']
        resource_name = 'product'
        fields = ['id', 'quantity', 'summary', 'description', 'deposit_amount']
        filtering = {
            'category': ALL_WITH_RELATIONS,
            'owner': ALL_WITH_RELATIONS,
        }
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(ProductResource, self).build_filters(filters)

        if "q" in filters or "l" in filters:
            sqs = product_search

            if "q" in filters:
                sqs = sqs.auto_query(filters['q'])

            if "l" in filters:
                name, (lat, lon) = GoogleGeocoder().geocode(filters['l'])
                radius = filters.get('r', DEFAULT_RADIUS)
                if lat and lon:
                    sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')

            orm_filters.update({"pk__in": [i.pk for i in sqs]})

        for kw in ["date_start", "date_end", "q", "l", "r"]:
            if kw in filters: del orm_filters[kw]

        return orm_filters
    
    def obj_create(self, bundle, **kwargs):
        """
        On product creation, if the request contains a "picture" parameter
        Creates a file with the content of the field
        And creates a picture linked to the product
        """
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage

        picture_data = bundle.data.get("picture", None)
        day_price_data = bundle.data.get("day_price", None)
        if picture_data:
            bundle.data.pop("picture")
        updated_bundle = UserSpecificResource.obj_create(self, bundle, **kwargs)

        # Create the picture object if there is a picture in the request
        if picture_data:
            picture = Picture(product=updated_bundle.obj)
            # Write the image content to a file
            img_path = upload_to(picture, "")
            img_file = ContentFile(decodestring(picture_data))
            img_path = default_storage.save(img_path, img_file)
            picture.image.name = img_path
            picture.save()

        # Add a day price to the object if there isnt any yet
        if day_price_data:
            Price(product=updated_bundle.obj, unit=1, amount=int(day_price_data)).save()

        return updated_bundle
    
    def dehydrate(self, bundle, request=None):
        """
        Automatically add the location price if the request
        contains date_start and date_end parameters
        """
        from datetime import datetime, timedelta
        from dateutil import parser

        if "date_start" in request.GET and "date_end" in request.GET:
            date_start = parser.parse(unquote(request.GET["date_start"]))
            date_end = parser.parse(unquote(request.GET["date_end"]))
        else:
            date_start = datetime.now() + timedelta(days=1)
            date_end = date_start + timedelta(days=1)

        bundle.data["price"] = Booking.calculate_price(bundle.obj, date_start, date_end)
        return bundle
    

api_v1 = Api(api_name='1.0')
api_v1.register(CategoryResource())
api_v1.register(ProductResource())
api_v1.register(AddressResource())
api_v1.register(PhoneNumberResource())
api_v1.register(PictureResource())
api_v1.register(PriceResource())
api_v1.register(UserResource())
