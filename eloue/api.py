# -*- coding: utf-8 -*-
import logbook
import plistlib
from urllib import unquote
from base64 import decodestring
from decimal import Decimal as D

from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpCreated
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import dict_strip_unicode_keys

from oauth_provider.consts import OAUTH_PARAMETERS_NAMES
from oauth_provider.store import store, InvalidTokenError, InvalidConsumerError
from oauth_provider.utils import get_oauth_request, verify_oauth_request

from django.conf import settings
from django.conf.urls.defaults import url
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db import IntegrityError

from eloue.geocoder import GoogleGeocoder
from eloue.products.models import Product, Category, Picture, Price, upload_to#, StaticPage
from eloue.products.search_indexes import product_search
from eloue.accounts.models import Address, PhoneNumber, Patron, PHONE_TYPES
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
        print "IN IS AUTHENTICATED"
        if is_valid_request(request, ['oauth_consumer_key']):
            # Just checking if you're allowed to be there
            oauth_request = get_oauth_request(request)
            try:
                consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                print "RETURN TRUE"
                return True
            except InvalidConsumerError:
                print "INVALIDCONSUMERERROR RETURN FALSE"
                return False
        print "RETURN FALSE"
        return False


class OAuthAuthorization(Authorization):

    def is_authorized(self, request, object=None):

        if is_valid_request(request, ['oauth_consumer_key']):  # Read-only part
            print "REQUEST IS VALID 1"
            oauth_request = get_oauth_request(request)

            klass = self.resource_meta.object_class
            # Allow GET access to products and POST access to Patron for unlogged users
            if (issubclass(klass, Patron) and request.method == 'POST')\
                or (issubclass(klass, Product) and request.method == 'GET'):
                try:
                    consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                    print "RETURN TRUE"
                    return True
                except InvalidConsumerError:
                    print "RETURN FALSE"
                    return False

        if is_valid_request(request):  # Read/Write part
            oauth_request = get_oauth_request(request)
            consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
            try:
                token = store.get_access_token(request, oauth_request, consumer, oauth_request.get_parameter('oauth_token'))
            except InvalidTokenError:
                return False

            if not verify_oauth_request(request, oauth_request, consumer, token=token):
                return False

            if consumer and token:
                request.user = token.user.patron
                return True

        print "REQUEST NOT VALID"
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
    USER_FIELD_NAME = "user"

    def obj_get_list(self, request=None, **kwargs):
        # Get back the user object injected in get_list, and add it to the filters
        # If FILTER_GET_REQUESTS is true
        filters = None

        if hasattr(request, 'GET'):
            filters = request.GET.copy()

        if self.FILTER_GET_REQUESTS:
            filters[self.USER_FIELD_NAME] = request.user

        applicable_filters = self.build_filters(filters=filters)

        try:
            return self.get_object_list(request).filter(**applicable_filters)

        except ValueError:
            raise NotFound("Invalid resource lookup data provided (mismatched type).")

    def build_filters(self, filters):
        orm_filters = {}
        filters = super(UserSpecificResource, self).build_filters(filters)
        user = filters.pop(self.USER_FIELD_NAME) if self.USER_FIELD_NAME in filters else None

        if not self.FILTER_GET_REQUESTS:
            return filters

        if user:
            orm_filters['patron'] = user

        return orm_filters

class UserResource(OAuthResource):

    class Meta(MetaBase):
        queryset = Patron.objects.all()
        resource_name = "user"
        allowed_methods = ['get', 'post', 'put', 'delete']
        fields = ['username', 'id', 'email']
        filtering = {
            'username': ALL_WITH_RELATIONS,
            'email': ALL_WITH_RELATIONS
        }


    def obj_create(self, bundle, request=None, **kwargs):
        """Creates a new inactive user"""

        print "IN OBJ CREATE"
        data = bundle.data
        try:
            print data
            bundle.obj = Patron.objects.create_user(data["username"], data["email"], data["password"])
        except IntegrityError:
            print "INTEGRITY ERROR"
            raise ImmediateHttpResponse(response=HttpBadRequest())
        except Exception, e:
            print "OTHER EXCEPTION", e
            print type(e)
            raise ImmediateHttpResponse(response=HttpBadRequest())

        return bundle

    def obj_get_list(self, request=None, **kwargs):
        raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_update(self, bundle, request=None, pk='', **kwargs):
        pk = int(pk)
        patron = Patron.objects.get(id=pk)
        if patron == request.user:
            for field in ("email", "username"):
                if field in bundle.data:
                    setattr(patron, field, bundle.data[field])
                    patron.save()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_delete(self, request=None, pk='', **kwargs):
        pk = int(pk)
        patron = Patron.objects.get(id=pk)
        if patron == request.user:
            patron.delete()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())


class CustomerResource(UserResource):

    class Meta(UserResource.Meta):
        resource_name = "customer"

    def obj_get_list(self, request=None, **kwargs):
        user = request.user
        return user.customers.all()

    def obj_create(self, bundle, request=None, **kwargs):
        """Creates a new inactive user"""

        bundle = super(CustomerResource, self).obj_create(bundle, request, **kwargs)
        user = request.user

        if not user.is_anonymous():
            user.customers.add(bundle.obj)

        return bundle

class PhoneNumberResource(UserSpecificResource):
    """Resource that sends back the phone numbers linked to the user"""
    patron = fields.ForeignKey(UserResource, 'patron', full=False, null=True)

    class Meta(MetaBase):
        queryset = PhoneNumber.objects.all()
        resource_name = "phonenumber"
        allowed_methods = ['get', 'post', 'put', 'delete']

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data['patron'] = UserResource().get_resource_uri(request.user)
        bundle.data['kind'] = getattr(PHONE_TYPES, bundle.data['kind'])
        print bundle.data['patron']
        return super(PhoneNumberResource, self).obj_create(bundle, request, **kwargs)

    def obj_update(self, bundle, request=None, pk='', **kwargs):
        print "IN OBJ UPDATE"
        pk = int(pk)
        number = PhoneNumber.objects.filter(id=pk)
        if number[0].patron == request.user:
                number.update(**bundle.data)
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_delete(self, request=None, pk='', **kwargs):
        pk = int(pk)
        number = PhoneNumber.objects.get(id=pk)
        if number.patron == request.user:
            number.delete()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())


class AddressResource(UserSpecificResource):
    """Resource that sends back the addresses linked to the user"""
    patron = fields.ForeignKey(UserResource, 'patron', full=False, null=True)

    class Meta(MetaBase):
        queryset = Address.objects.all()
        resource_name = "address"
        allowed_methods = ['get', 'post', 'put', 'delete']

    def dehydrate(self, bundle, request=None):
        if bundle.obj.position:
            bundle.data["position"] = {'lat': bundle.obj.position.x, 'lng': bundle.obj.position.y}
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data['patron'] = UserResource().get_resource_uri(request.user)
        return super(AddressResource, self).obj_create(bundle, request, **kwargs)

    def obj_delete(self, request=None, pk='', **kwargs):
        pk = int(pk)
        address = Address.objects.get(id=pk)
        if address.patron == request.user:
            address.delete()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_update(self, bundle, request=None, pk='', **kwargs):
        pk = int(pk)
        address = Address.objects.filter(id=pk)
        if address[0].patron == request.user:
            address.update(**bundle.data)
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())


class CategoryResource(ModelResource):
    parent = fields.ForeignKey('self', 'parent', full=False, null=True)

    class Meta:
        queryset = Category.on_site.all()
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
        nodes = []
        for root in roots:
            nodes.extend(root.get_children())
        return [build_node(node) for node in nodes]

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
    distance = fields.RelatedField(Distance, 'distance', null=True)

    FILTER_GET_REQUESTS = False

    class Meta(MetaBase):
        queryset = Product.on_site.all()
        allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'product'
        include_absolute_url = True
        fields = ['id', 'quantity', 'summary', 'description', 'deposit_amount']
        ordering = ['distance']
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

    def post_list(self, request, **kwargs):
        """Stop making it return standard location header"""
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized))
        self.is_valid(bundle, request)
        updated_bundle = self.obj_create(bundle, request=request)
        return HttpCreated(location=updated_bundle.obj.get_absolute_url())

    def get_object_list(self, request):
        object_list = super(ProductResource, self).get_object_list(request)
        if "l" in request.GET:
            name, (lat, lon), radius = GoogleGeocoder().geocode(request.GET['l'])
            object_list = object_list.distance(Point((lat, lon)), field_name='address__position')
        return object_list

    def _obj_process_fields(self, product, picture_data, day_price_data):

        # Create the picture object if there is a picture in the request
        if picture_data:
            picture = Picture(product=product)

            # Write the image content to a file
            img_path = upload_to(picture, "")
            img_file = ContentFile(decodestring(picture_data))
            img_path = default_storage.save(img_path, img_file)
            picture.image.name = img_path
            picture.save()

        # Add a day price to the object if there isnt any yet
        if day_price_data:
            Price(product=product, unit=1, amount=D(day_price_data)).save()


    def obj_create(self, bundle, request=None, **kwargs):
        """
        On product creation, if the request contains a "picture" parameter
        Creates a file with the content of the field
        And creates a picture linked to the product
        """
        picture_data = bundle.data.pop("picture", None)
        day_price_data = bundle.data.pop("price", None)

        if picture_data:
            bundle.data.pop("picture")

        bundle.data['owner'] = UserResource().get_resource_uri(request.user)
        bundle = super(ProductResource, self).obj_create(bundle, request, **kwargs)

        self._obj_process_fields(bundle.obj, picture_data, day_price_data)

        return bundle

    def obj_update(self, bundle, request=None, pk='', **kwargs):
        try:
            p_id = pk.split("-")[-1]
            product = Product.objects.filter(id=int(p_id))
            if product[0].owner == request.user:
                picture_data = bundle.data.pop("picture", None)
                day_price_data = bundle.data.pop("price", None)
                product.update(**bundle.data)

                self._obj_process_fields(bundle.obj, picture_data, day_price_data)
                return bundle
            else:
                raise ImmediateHttpResponse(response=HttpBadRequest())
        except Exception, e:
            print e
            print e.message

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

        if bundle.data["distance"]:
            bundle.data["distance"] = bundle.data["distance"].km
        bundle.data["unit"], bundle.data["price"] = Booking.calculate_price(bundle.obj, date_start, date_end)
        return bundle


api_v1 = Api(api_name='1.0')
api_v1.register(CategoryResource())
api_v1.register(ProductResource())
api_v1.register(AddressResource())
api_v1.register(PhoneNumberResource())
api_v1.register(PictureResource())
api_v1.register(PriceResource())
api_v1.register(UserResource())
api_v1.register(CustomerResource())
