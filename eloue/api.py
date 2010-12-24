# -*- coding: utf-8 -*-
import logbook
import plistlib
from urllib import unquote
from base64 import decodestring

from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from oauth_provider.consts import OAUTH_PARAMETERS_NAMES
from oauth_provider.store import store, InvalidTokenError, InvalidConsumerError
from oauth_provider.utils import get_oauth_request, verify_oauth_request

from django.conf import settings
from django.conf.urls.defaults import url
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from eloue.geocoder import GoogleGeocoder
from eloue.products.models import Product, Category, Picture, Price, upload_to
from eloue.products.search_indexes import product_search
from eloue.accounts.models import Address, PhoneNumber, Patron
from eloue.rent.models import Booking

__all__ = ['api_v1']

log = logbook.Logger('eloue.api')

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


def is_valid_request(request, parameters=OAUTH_PARAMETERS_NAMES):
    """
    Checks whether the required parameters are either in
    the http-authorization header sent by some clients,
    which is by the way the preferred method according to
    OAuth spec, but otherwise fall back to `GET` and `POST`.
    """
    is_in = lambda l: all((p in l) for p in parameters)
    auth_params = request.META.get("HTTP_AUTHORIZATION", [])
    return is_in(auth_params) or is_in(request.REQUEST)


class OAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if is_valid_request(request, ['oauth_consumer_key']):
            # Just checking if you're allowed to be there
            oauth_request = get_oauth_request(request)
            try:
                consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                return True
            except InvalidConsumerError:
                return False
        return False
    

class OAuthAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if is_valid_request(request, ['oauth_consumer_key']):  # Read-only part
            oauth_request = get_oauth_request(request)
            if issubclass(self.resource_meta.object_class, Product) and request.method == 'GET':
                try:
                    consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                    return True
                except InvalidConsumerError:
                    return False
            if issubclass(self.resource_meta.object_class, Patron) and request.method == 'POST':
                try:
                    consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                    return True
                except InvalidConsumerError:
                    return False
        if is_valid_request(request):  # Read/Write part
            oauth_request = get_oauth_request(request)
            consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
            try:
                token = store.get_access_token(request, oauth_request, consumer, oauth_request.get_parameter('oauth_token'))
            except InvalidTokenError, e:
                return False
        
            if not verify_oauth_request(request, oauth_request, consumer, token=token):
                return False
            
            if consumer and token:
                request.user = token.user.patron
                return True
        return False
    

class JSONSerializer(Serializer):
    formats = ['json', 'jsonp']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
    }


class PlistSerializer(Serializer):
    formats = ['json', 'jsonp', 'plist']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'plist': 'text/plist'
    }
    
    def to_simple(self, data, options):
        if isinstance(data, dict):
            data = dict((key, self.to_simple(val, options)) for (key, val) in data.iteritems() if val)
        return super(PlistSerializer, self).to_simple(data, options)
    
    def to_plist(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        
        return plistlib.writePlistToString(data)
    
    def from_plist(self, content):
        return plistlib.readPlistFromString(content)
    

class MetaBase():
    """Define meta attributes that must be shared between all resources"""
    authentication = OAuthentication()
    authorization = OAuthAuthorization()
    serializer = JSONSerializer()


class OAuthResource(ModelResource):
    def build_filters(self, filters=None):
        filters = super(OAuthResource, self).build_filters(filters)
        for key, val in filters.items():
            if key.startswith("oauth_"):
               del filters[key]
        return filters
    

class UserSpecificResource(OAuthResource):
    """
    Base class for a resource that restrain the possible actions to the scope of the user
    For GET: Only user owned objects are returned
    For POST: The objects created are automatically owned by the user
    """
    # TODO : Make it work the same way with obj_get than with get_list
    FILTER_GET_REQUESTS = True
    
    def obj_get_list(self, request=None, **kwargs):
        # Get back the user object injected in get_list, and add it to the filters
        # If FILTER_GET_REQUESTS is true
        filters = None
        
        if hasattr(request, 'GET'):
            filters = request.GET.copy()
        
        if self.FILTER_GET_REQUESTS:
            filters["user"] = request.user
        
        applicable_filters = self.build_filters(filters=filters)
        
        try:
            return self.get_object_list(request).filter(**applicable_filters)
        except ValueError, e:
            raise NotFound("Invalid resource lookup data provided (mismatched type).")
    
    def build_filters(self, filters):
        orm_filters = {}
        filters = super(UserSpecificResource, self).build_filters(filters)
        user = filters.pop("user") if "user" in filters else None
        
        if not self.FILTER_GET_REQUESTS:
            return filters
        
        if user:
            orm_filters['patron'] = user
        
        return orm_filters
    

class UserResource(OAuthResource):
    class Meta(MetaBase):
        queryset = Patron.objects.all()
        resource_name = "user"
        allowed_methods = ['get', 'post']
        fields = ['username', 'id', 'email']
        filtering = {
            'username': ALL_WITH_RELATIONS,
            'email': ALL_WITH_RELATIONS
        }
    
    def obj_create(self, bundle, **kwargs):
        """Creates a new inactive user"""
        data = bundle.data
        bundle.obj = Patron.objects.create_user(data["username"], data["email"], data["password"])
        return bundle
    

class PhoneNumberResource(UserSpecificResource):
    """Resource that sends back the phone numbers linked to the user"""
    patron = fields.ForeignKey(UserResource, 'patron', full=False, null=True)
    
    class Meta(MetaBase):
        queryset = PhoneNumber.objects.all()
        resource_name = "phonenumber"
        allowed_methods = ['get', 'post']
    
    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data['patron'] = UserResource().get_resource_uri(request.user)
        return super(AddressResource, self).obj_create(bundle, request, **kwargs)
    

class AddressResource(UserSpecificResource):
    """Resource that sends back the addresses linked to the user"""
    patron = fields.ForeignKey(UserResource, 'patron', full=False, null=True)
    
    class Meta(MetaBase):
        queryset = Address.objects.all()
        resource_name = "address"
        allowed_methods = ['get', 'post']
    
    def dehydrate(self, bundle, request=None):
        if bundle.obj.position:
            bundle.data["position"] = {'lat': bundle.obj.position.x, 'lng': bundle.obj.position.y}
        return bundle
    
    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data['patron'] = UserResource().get_resource_uri(request.user)
        return super(AddressResource, self).obj_create(bundle, request, **kwargs)
    

class CategoryResource(ModelResource):
    parent = fields.ForeignKey('self', 'parent', full=False, null=True)
    
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']
        fields = ['id', 'name', 'slug']
        filtering = {
            "id": ALL_WITH_RELATIONS,
            "parent": ALL_WITH_RELATIONS,
        }
        serializer = PlistSerializer()
    
    def build_tree(self):
        def build_node(node):
            bits = []
            for child in node.get_children():
                bits.append(build_node(child))
            bundle = self.full_dehydrate(node)
            bundle.data['children'] = bits
            return bundle.data
        roots = Category.tree.root_nodes()
        return [build_node(node) for node in roots]
    
    def get_tree(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        return self.create_response(request, self.build_tree())
    
    def base_urls(self):
        return super(CategoryResource, self).base_urls()
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/tree/$" % self._meta.resource_name, self.wrap_view('get_tree'), name="api_get_tree"),
        ]
    

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
    
    FILTER_GET_REQUESTS = False
    
    class Meta(MetaBase):
        queryset = Product.objects.all()
        allowed_methods = ['get', 'post']
        resource_name = 'product'
        include_absolute_url = True
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
                name, (lat, lon), radius = GoogleGeocoder().geocode(filters['l'])
                radius = filters.get('r', radius if radius else DEFAULT_RADIUS)
                if lat and lon:
                    sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
            
            pk = []
            for p in sqs:
                try:
                    pk.append(int(p.pk))
                except ValueError:
                    pass
            
            orm_filters.update({"pk__in": pk})
        
        return orm_filters
    
    def obj_create(self, bundle, request=None, **kwargs):
        """
        On product creation, if the request contains a "picture" parameter
        Creates a file with the content of the field
        And creates a picture linked to the product
        """
        picture_data = bundle.data.get("picture", None)
        day_price_data = bundle.data.get("day_price", None)
        if picture_data:
            bundle.data.pop("picture")
        
        bundle.data['owner'] = UserResource().get_resource_uri(request.user)
        bundle = super(ProductResource, self).obj_create(bundle, request, **kwargs)
        
        # Create the picture object if there is a picture in the request
        if picture_data:
            picture = Picture(product=bundle.obj)
            # Write the image content to a file
            img_path = upload_to(picture, "")
            img_file = ContentFile(decodestring(picture_data))
            img_path = default_storage.save(img_path, img_file)
            picture.image.name = img_path
            picture.save()
        
        # Add a day price to the object if there isnt any yet
        if day_price_data:
            Price(product=bundle.obj, unit=1, amount=int(day_price_data)).save()
        
        return bundle
    
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
