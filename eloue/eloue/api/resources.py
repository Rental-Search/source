# -*- coding: utf-8 -*-

import re
import logbook
import plistlib
from urllib import unquote,quote,urlencode
from base64 import decodestring
from decimal import Decimal as D

from django_fsm.db.fields import transition

from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpCreated, HttpAccepted
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import dict_strip_unicode_keys

from oauth_provider.consts import OAUTH_PARAMETERS_NAMES
from oauth_provider.store import store, InvalidTokenError, InvalidConsumerError
from oauth_provider.utils import get_oauth_request, verify_oauth_request

from django.conf import settings
from django.conf.urls import url
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from products.models import Product, Category, Picture, Price, upload_to, PAYMENT_TYPE, ProductRelatedMessage, MessageThread, UNIT#, StaticPage
from products.search_indexes import product_search
from accounts.models import Address, PhoneNumber, Patron, PHONE_TYPES
from rent.models import Booking

from eloue.geocoder import GoogleGeocoder
from eloue.utils import json

__all__ = ['api_v1']

log = logbook.Logger('eloue.api')

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


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
                
                try:
                    if oauth_request.get_parameter('oauth_token'):
                        try:
                            token = store.get_access_token(request, oauth_request, consumer, oauth_request.get_parameter('oauth_token'))

                            if not verify_oauth_request(request, oauth_request, consumer, token=token):
                                return False

                            if consumer and token:
                                request.user = token.user.patron

                        except InvalidTokenError:
                            return False
                except:
                    pass

                return True

            except InvalidConsumerError:
                return False
        return False


class OAuthAuthorization(Authorization):

    def _is_valid(self, request):

        if is_valid_request(request):  # Read/Write part
            if request.user:
                return True
            else:
                return False

        return False


    def is_authorized(self, request):

        if is_valid_request(request, ['oauth_consumer_key']):  # Read-only part
            oauth_request = get_oauth_request(request)

            klass = self.resource_meta.object_class
            # Allow GET access to products and POST access to Patron for unlogged users
            if (issubclass(klass, Patron) and request.method == 'POST')\
                or (issubclass(klass, Product) and request.method == 'GET'):
                try:
                    consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                    return True
                except InvalidConsumerError:
                    return False

            return self._is_valid(request)


    def read_list(self, object_list, bundle):
        if self.is_authorized(bundle.request):
            return object_list
        else:
            return []

    def read_detail(self, object_list, bundle):
        return self.is_authorized(bundle.request)

    def create_list(self, object_list, bundle):
        if self.is_authorized(bundle.request):
            return object_list
        else:
            return []

    def create_detail(self, object_list, bundle):
        return self.is_authorized(bundle.request)

    def update_list(self, object_list, bundle):
        if self.is_authorized(bundle.request):
            return object_list
        else:
            return []

    def update_detail(self, object_list, bundle):
        return self.is_authorized(bundle.request)

    def delete_list(self, object_list, bundle):
        if self.is_authorized(bundle.request):
            return object_list
        else:
            return []

    def delete_detail(self, object_list, bundle):
        return self.is_authorized(bundle.request)



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

    def obj_get_list(self, bundle, **kwargs):
        # Get back the user object injected in get_list, and add it to the filters
        # If FILTER_GET_REQUESTS is true
        filters = None

        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()

        if self.FILTER_GET_REQUESTS:
            filters[self.USER_FIELD_NAME] = bundle.request.user

        applicable_filters = self.build_filters(filters=filters)

        try:
            return self.get_object_list(bundle.request).filter(**applicable_filters)

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
        fields = ['username', 'id', 'email', 'first_name', 'last_name']
        filtering = {
            'username': ALL_WITH_RELATIONS,
            'email': ALL_WITH_RELATIONS
        }


    def obj_create(self, bundle, **kwargs):
        """Creates a new inactive user"""

        data = bundle.data
        try:
            bundle.obj = Patron.objects.create_user(data["username"], data["email"], data["password"])
        except IntegrityError:
            raise ImmediateHttpResponse(response=HttpBadRequest())
        except Exception, e:
            raise ImmediateHttpResponse(response=HttpBadRequest())

        return bundle

    def obj_update(self, bundle, pk='', **kwargs):
        pk = int(pk)
        patron = Patron.objects.get(id=pk)
        if patron == bundle.request.user:
            for field in ("email", "username"):
                if field in bundle.data:
                    setattr(patron, field, bundle.data[field])
                    patron.save()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_delete(self, pk='', **kwargs):
        pk = int(pk)
        patron = Patron.objects.get(id=pk)
        if patron == bundle.request.user:
            patron.delete()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())


class CustomerResource(UserResource):

    class Meta(UserResource.Meta):
        resource_name = "customer"

    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.user
        return user.customers.all()

    def obj_create(self, bundle, **kwargs):
        """Creates a new inactive user"""

        bundle = super(CustomerResource, self).obj_create(bundle, **kwargs)
        user = bundle.request.user

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

    def obj_create(self, bundle, **kwargs):
        bundle.data['patron'] = UserResource().get_resource_uri(bundle.request.user)
        bundle.data['kind'] = getattr(PHONE_TYPES, bundle.data['kind'])
        return super(PhoneNumberResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, pk='', **kwargs):
        pk = int(pk)
        number = PhoneNumber.objects.filter(id=pk)
        if number[0].patron == bundle.request.user:
                number.update(**bundle.data)
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_delete(self, pk='', **kwargs):
        pk = int(pk)
        number = PhoneNumber.objects.get(id=pk)
        if number.patron == bundel.request.user:
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

    def dehydrate(self, bundle):
        if bundle.obj.position:
            bundle.data["position"] = {'lat': bundle.obj.position.x, 'lng': bundle.obj.position.y}
        return bundle

    def obj_create(self, bundle, **kwargs):
        bundle.data['patron'] = UserResource().get_resource_uri(bundle.request.user)
        return super(AddressResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, pk='', **kwargs):
        pk = int(pk)
        address = Address.objects.get(id=pk)
        if address.patron == bundle.request.user:
            address.delete()
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def obj_update(self, bundle, pk='', **kwargs):
        pk = int(pk)
        address = Address.objects.filter(id=pk)
        if address[0].patron == bundle.request.user:
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
            bundle = self.full_dehydrate(self.build_bundle(node))
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

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/tree/$" % self._meta.resource_name, self.wrap_view('get_tree'), name="api_get_tree"),
        ]

class PictureResource(OAuthResource):
    class Meta:
        queryset = Picture.objects.all()
        resource_name = 'picture'
        allowed_methods = ['get']
        fields = ['id']

    def dehydrate(self, bundle):
        bundle.data['thumbnail_url'] = bundle.obj.thumbnail.url
        bundle.data['display_url'] = bundle.obj.display.url
        return bundle


class PriceResource(OAuthResource):
    class Meta(MetaBase):
        queryset = Price.objects.all()
        resource_name = "price"
        fields = ["amount", "currency", "unit"]
        allowed_methods = ['get', 'post']

    def dehydrate(self, bundle):
        bundle.data["unit"] = UNIT.reverted[bundle.data["unit"]]
        return bundle

    def hydrate(self, bundle):
        bundle.obj.unit = UNIT.enum_dict[bundle.data["unit"]]


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
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        self.is_valid(bundle)
        updated_bundle = self.obj_create(bundle, request=request)
        return HttpCreated(location=updated_bundle.obj.get_absolute_url())

    def get_object_list(self, request):
        object_list = super(ProductResource, self).get_object_list(request)
        if request and "l" in request.GET:
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

    def add_prices(self, bundle, prices):
        from dateutil.parser import parse
        if prices:
            bundle.obj.prices.all().delete()
            for price_dict in prices:
                price_dict["unit"] = UNIT.enum_dict[price_dict["unit"]]
                price_dict["started_at"] = parse(price_dict["started_at"])
                price_dict["ended_at"] = parse(price_dict["ended_at"])
                price = Price(product=bundle.obj, **price_dict)
                price.save()

    def obj_create(self, bundle, **kwargs):
        """
        On product creation, if the request contains a "picture" parameter
        Creates a file with the content of the field
        And creates a picture linked to the product
        """
        picture_data = bundle.data.pop("picture", None)
        day_price_data = bundle.data.pop("price", None)
        prices = bundle.data.pop("prices", None)

        bundle.data['owner'] = UserResource().get_resource_uri(bundle.request.user)
        bundle = super(ProductResource, self).obj_create(bundle, **kwargs)

        self._obj_process_fields(bundle.obj, picture_data, day_price_data)
        self.add_prices(bundle, prices)

        return bundle

    def obj_update(self, bundle, pk='', **kwargs):
        p_id = pk.split("-")[-1]
        product = Product.objects.filter(id=int(p_id))
        if product[0].owner == bundle.request.user:
            picture_data = bundle.data.pop("picture", None)
            day_price_data = bundle.data.pop("price", None)
            prices = bundle.data.pop("prices", None)
            bundle = super(ProductResource, self).obj_update(bundle, pk=p_id, **kwargs)

            self.add_prices(bundle, prices)
            self._obj_process_fields(bundle.obj, picture_data, day_price_data)
            return bundle
        else:
            raise ImmediateHttpResponse(response=HttpBadRequest())

    def dehydrate(self, bundle):
        """
        Automatically add the rent price if the request
        contains date_start and date_end parameters
        """
        from datetime import datetime, timedelta
        from dateutil import parser

        request = bundle.request
        if request and "date_start" in request.GET and "date_end" in request.GET:
            date_start = parser.parse(unquote(request.GET["date_start"]))
            date_end = parser.parse(unquote(request.GET["date_end"]))
        else:
            date_start = datetime.now() + timedelta(days=1)
            date_end = date_start + timedelta(days=1)

        if bundle.data["distance"]:
            bundle.data["distance"] = bundle.data["distance"].km
        bundle.data["unit"], bundle.data["price"] = Booking.calculate_price(bundle.obj, date_start, date_end)
        return bundle


def require_keys(keys, data):
    if set(keys) != set(data.keys()):
        raise ImmediateHttpResponse(response=HttpBadRequest("Your request didn't meet the specs"))


class BookingResource(OAuthResource):
    """
    Resource that returns the booking information
    """
    # Foreign keys
    owner = fields.ForeignKey(UserResource,'owner', full=False, null=True)
    borrower = fields.ForeignKey(UserResource,'borrower', full=False, null=True)
    product = fields.ForeignKey(ProductResource,'product', full=False, null=True)

    # Meta 
    class Meta(MetaBase):
        queryset = Booking.on_site.all()
        list_allowed_methods = ['get', 'post','put']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'booking'
        always_return_data = True
        excludes = ["pay_key"]
        filtering = {
            'owner': ALL_WITH_RELATIONS,
            'borrower': ALL_WITH_RELATIONS,
            'product': ALL_WITH_RELATIONS,
            'ended_at': ALL_WITH_RELATIONS,
            'started_at': ALL_WITH_RELATIONS,
        }

    def obj_create(self, bundle, **kwargs):

        from dateutil import parser

        is_offline_booking = bool(bundle.data.pop("is_offline_booking", False))

        require_keys(["product", "started_at", "ended_at"], bundle.data)
        product = Product.objects.get(pk=int(bundle.data["product"].split('/')[-2]))
        started_at = parser.parse(unquote(bundle.data["started_at"]))
        ended_at = parser.parse(unquote(bundle.data["ended_at"]))
        unit, total_amount = Booking.calculate_price(product, started_at, ended_at)
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        state = "authorized" if product.owner == bundle.request.user else "authorizing"

        bundle = super(BookingResource, self).obj_create(bundle,
            state= state,
            owner=product.owner,
            borrower=bundle.request.user,
            total_amount=total_amount,
            **kwargs
        )

        # Pass unit information to dehydrate
        bundle.data["price_unit"] = UNIT.reverted[unit]

        if not is_offline_booking and state == "authorizing":
            try:
                booking = bundle.obj
                booking.init_payment_processor()
                booking.preapproval(
                    cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
                    return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
                    ip_address=request.META['REMOTE_ADDR']
                )
            except IntegrityError:
                raise ImmediateHttpResponse(response=HttpBadRequest())

        return bundle

    def obj_update(self, bundle, pk='', **kwargs):

        is_offline_booking = bool(bundle.data.pop("is_offline_booking", False))
        require_keys(["state"], bundle.data)

        new_state = bundle.data["state"].lower()
        booking = Booking.objects.get(pk=pk)

        def error(error_str):
            raise ImmediateHttpResponse(
                response = HttpResponseBadRequest(
                    content_type='application/json',
                    content=json.dumps({ "error":error_str })
                )
            )

        def assert_current_state_is(from_state):

            if type(from_state) is list:
                wrong_status = booking.state not in from_state
            else:
                wrong_status = booking.state != from_state

            if wrong_status:
                raise ImmediateHttpResponse(
                    response=error("Need to be in state %s to switch to state %s" % (from_state, booking.state))
                )

        if booking.owner != bundle.request.user:
            error("Can't modify booking : Wrong user")

        if new_state == 'pending':

            if booking.product.payment_type == PAYMENT_TYPE.PAYPAL:
                is_valid = booking.owner.is_valid
                is_confirmed = booking.owner.is_confirmed
                if not booking.owner.has_paypal():
                    return error("The owner doesn't have paypal account")
                elif not is_verified:
                    return error("The owner's paypal account is invalid")
                elif not is_confirmed:
                    return error("The owner's paypal email is not confirmed")

            assert_current_state_is("authorized")
            booking.send_acceptation_email()
            GoalRecord.record('rent_object_accepted', WebUser(bundle.request))

        elif new_state == 'rejected':
            assert_current_state_is("authorized")
            booking.send_rejection_email()
            GoalRecord.record('rent_object_rejected', WebUser(bundle.request))

        elif new_state == 'closed':
            assert_current_state_is(["closing", "ongoing"])
            if not is_offline_booking:
                booking.init_payment_processor()
                booking.pay()


        return super(BookingResource, self).obj_update(bundle, request=bundle.request, pk=pk, **kwargs)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter( Q(borrower=request.user) | Q(owner=request.user) )

    def dehydrate(self, bundle):
        """
        Modify the data before sending it to the client
        """
        bundle.data["preapproval_url"] = settings.PAYPAL_COMMAND % urlencode({'cmd': '_ap-preapproval','preapprovalkey': bundle.data["preapproval_key"]})
        return bundle

class MessageResource(OAuthResource):
    # Foreign keys
    recipient = fields.ForeignKey(UserResource,'recipient', full=False, null=True)
    sender = fields.ForeignKey(UserResource,'sender', full=False, null=True)
    parent_msg = fields.ForeignKey('self','parent_msg', full=False, null=True)

    class Meta(MetaBase):
        queryset = ProductRelatedMessage.objects.all()
        resource_name = "message"
        fields = []
        allowed_methods = ['get', 'post']

    def obj_get_list(self, bundle, **kwargs):
        object_list = self.get_object_list(bundle.request).filter( Q(recipient=bundle.request.user) | Q(sender=bundle.request.user) )
        return object_list

    def obj_create(self, bundle, **kwargs):
        data = bundle.data

        try:
            recipient = Patron.objects.get(id=int(data["recipient"].split("/")[-2]))
            parent_msg = ProductRelatedMessage.objects.get(id=int(data["parent_msg"].split("/")[-2]))
            thread = MessageThread.objects.get(id=int(data["thread"]))
            bundle.obj=ProductRelatedMessage(recipient = recipient,
                                sender = bundle.request.user,
                                parent_msg = parent_msg,
                                subject = data["subject"],
                                body = data["body"],
                                thread = thread
                      )
        except IntegrityError:
            raise ImmediateHttpResponse(response=HttpBadRequest())
        return bundle

    def post_list(self, request, **kwargs):
        post_data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        bundle = self.build_bundle(data=dict_strip_unicode_keys(post_data), request=request)
        self.is_valid(bundle)
        updated_bundle = self.obj_create(bundle)
        if updated_bundle.obj.sender is updated_bundle.obj.recipient:
            error_message = "You can't send message to yourself"
            cont_dic = {"error":error_message}
            content = json.dumps(cont_dic)
            return HttpResponseBadRequest(content_type='application/json', content=content)
        updated_bundle.obj.save()
        return HttpCreated(location = updated_bundle.obj.get_absolute_url())


api_v1 = Api(api_name='1.0')
api_v1.register(CategoryResource())
api_v1.register(ProductResource())
api_v1.register(AddressResource())
api_v1.register(PhoneNumberResource())
api_v1.register(PictureResource())
api_v1.register(PriceResource())
api_v1.register(UserResource())
api_v1.register(CustomerResource())
api_v1.register(BookingResource())
api_v1.register(MessageResource())
