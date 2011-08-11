# -*- coding: utf-8 -*-
import logbook
import plistlib
from urllib import unquote,quote,urlencode
from base64 import decodestring
from decimal import Decimal as D
import simplejson as json

from fsm import transition

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
from django.conf.urls.defaults import url
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

from eloue.geocoder import GoogleGeocoder
from eloue.products.models import Product, Category, Picture, Price, upload_to, PAYMENT_TYPE#, StaticPage
from eloue.products.search_indexes import product_search
from eloue.accounts.models import Address, PhoneNumber, Patron
from eloue.rent.models import Booking
from eloue.rent.views import preapproval_ipn, pay_ipn, booking_success, booking_failure

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
                #print oauth_request.get_parameter('oauth_consumer_key')
                consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                return True
            except InvalidConsumerError:
                return False
        return False
    

class OAuthAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        #print "enter"
        if is_valid_request(request, ['oauth_consumer_key']):  # Read-only part
            oauth_request = get_oauth_request(request)
            if issubclass(self.resource_meta.object_class, Product) and request.method == 'GET':
                try:
                    consumer = store.get_consumer(request, oauth_request, oauth_request.get_parameter('oauth_consumer_key'))
                    #print "2"
                    #print consumer
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
            except InvalidTokenError:
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
            #print "1"
            #print request.GET.copy()
            filters = request.GET.copy()
        
        if self.FILTER_GET_REQUESTS:
            #print "2"
            #print request.user
            filters["user"] = request.user
        #print "3"
        #print filters
        applicable_filters = self.build_filters(filters=filters)
        #applicable_filters = {"owner":request.user}
        #print "4"
        #print applicable_filters
        
        try:
            return self.get_object_list(request).filter(**applicable_filters)
        except ValueError:
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
        try:
            bundle.obj = Patron.objects.create_user(data["username"], data["email"], data["password"])
        except IntegrityError:
            raise ImmediateHttpResponse(response=HttpBadRequest())
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
        return super(PhoneNumberResource, self).obj_create(bundle, request, **kwargs)
    

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
        #print request.user
        #print ">>>>>>>>>>>>"
        #print UserResource().get_resource_uri(request.user)
        bundle.data['patron'] = UserResource().get_resource_uri(request.user)
        return super(AddressResource, self).obj_create(bundle, request, **kwargs)
    

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
        allowed_methods = ['get', 'post']
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
    
    def obj_create(self, bundle, request=None, **kwargs):
        """
        On product creation, if the request contains a "picture" parameter
        Creates a file with the content of the field
        And creates a picture linked to the product
        """
        picture_data = bundle.data.get("picture", None)
        day_price_data = bundle.data.get("price", None)
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
            Price(product=bundle.obj, unit=1, amount=D(day_price_data)).save()
        return bundle
    
    def dehydrate(self, bundle, request=None):
        """
        Automatically add the rent price if the request
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
        excludes = ["pay_key"]
        filtering = {
            'owner': ALL_WITH_RELATIONS,
            'borrower': ALL_WITH_RELATIONS,
            'product': ALL_WITH_RELATIONS,
            'ended_at': ALL_WITH_RELATIONS,
            'started_at': ALL_WITH_RELATIONS,
        }
    
    def obj_create(self, bundle,  request=None, **kwargs):
        """Creates the object for booking"""   
        from datetime import datetime, timedelta
        from dateutil import parser        
        data = bundle.data
        try:
            product = Product.objects.get(id=int(data["product"].split("/")[-2]))
            borrower = Patron.objects.get(id=int(data["borrower"].split("/")[-2]))
            started_at = parser.parse(unquote(data["started_at"]))
            ended_at = parser.parse(unquote(data["ended_at"]))

            temp, total_amount = Booking.calculate_price(product, started_at, ended_at)
            if data["status"] == "authorizing":
                bundle.obj=Booking(started_at = data["started_at"],  
                                    ended_at = data["ended_at"],  
                                    total_amount = total_amount,
                                    borrower = borrower,
                                    product = product,
                                    owner = product.owner,
                                  )
                bundle.obj.save()
            elif data['status'] and data["uuid"]:
                bundle.obj=Booking.objects.get(uuid=data["uuid"])
            else:
                # need to do some checking here
                pass
        except IntegrityError:
            raise ImmediateHttpResponse(response=HttpBadRequest())
        return bundle
    
    def post_list(self, request, **kwargs):
        """
        Set the returned response for created booking
        """
        post_data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        bundle = self.build_bundle(data=dict_strip_unicode_keys(post_data))
        self.is_valid(bundle, request)
        updated_bundle = self.obj_create(bundle, request=request)
        
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        payment_type = updated_bundle.obj.product.payment_type
        
        if post_data["status"].lower() == 'authorizing':
            try:
                booking = get_object_or_404(Booking, pk=updated_bundle.obj.uuid)
                booking.state = "authorizing"
                booking.init_payment_processor()
                booking.preapproval(
                    cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
                    return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
                    ip_address=request.META['REMOTE_ADDR']
                    )
                return HttpCreated(content_type='application/json', 
                                    location = "/api/1.0/booking/" + str(booking.uuid) + "/", 
                                    content = self.populate_response(booking) )
            except IntegrityError:
                raise ImmediateHttpResponse(response=HttpBadRequest())
                
        elif post_data["status"].lower() == 'pending' and updated_bundle.obj.uuid:
            booking = get_object_or_404(Booking, pk=updated_bundle.obj.uuid)
            if booking.product.payment_type == PAYMENT_TYPE.NOPAY:
                is_verified = booking.owner.is_verified
                if not booking.owner.has_paypal():
                    cont_dic = {"error":"The owner doesn't have paypal account"}
                    content = json.dumps(cont_dic)
                    return HttpResponse(content_type='application/json', content=content)                    
                elif is_verified!="VERIFIED":
                    if is_verified=="UNVERIFIED":
                        cont_dic = {"error":"The owner's paypal account is unverified"}
                        content = json.dumps(cont_dic)
                        return HttpResponse(content_type='application/json', content=content)
                    elif is_verified=="INVALID":
                        cont_dic = {"error":"The owner's paypal account is invalid"}                            
                        content = json.dumps(cont_dic)
                        return HttpResponse(content_type='application/json', content=content)
            if booking.state != "authorized":
                error_message = "can't switch from state "+ post_data["status"]+" to state pending"
                cont_dic = {"error":error_message}                            
                content = json.dumps(cont_dic)
                return HttpResponseBadRequest(content_type='application/json', content=content)
                  
            booking.state = post_data["status"]
            # TODO uncomment the following line 
            booking.send_acceptation_email()
            GoalRecord.record('rent_object_accepted', WebUser(request))
            booking.save()
            return HttpResponse(content_type='application/json', content=self.populate_response(booking))
            
        elif post_data["status"].lower() == 'rejected' and updated_bundle.obj.uuid:
            booking = get_object_or_404(Booking, pk=updated_bundle.obj.uuid)
            if booking.state != "authorized":
                error_message = "can't switch from state "+ post_data["status"]+" to state rejected"
                cont_dic = {"error":error_message}                            
                content = json.dumps(cont_dic)
                return HttpResponseBadRequest(content_type='application/json', content=content)
            booking.state = post_data["status"]
            # TODO uncomment the following line
            booking.send_rejection_email()
            GoalRecord.record('rent_object_rejected', WebUser(request))
            booking.save()
            return HttpResponse(content_type='application/json', content=self.populate_response(booking))
            
        elif post_data["status"].lower() == 'closed' and updated_bundle.obj.uuid:
            booking = get_object_or_404(Booking, pk=updated_bundle.obj.uuid)
            if booking.state != "closing":
                error_message = "can't switch from state "+ post_data["status"]+" to state closed"
                cont_dic = {"error":error_message}                            
                content = json.dumps(cont_dic)
                return HttpResponseBadRequest(content_type='application/json', content=content)
            booking.state=post_data["status"]
            # TODO uncomment the following lines
            booking.init_payment_processor()
            booking.pay()
            return HttpResponse(content_type='application/json', content=self.populate_response(booking))
        else: 
            pass
            
                
    def populate_response(self, booking):
        cont_dic = {}
        cont_dic["borrower"] = "/api/1.0/user/%s/" % booking.borrower.id
        cont_dic["canceled_at"] = booking.canceled_at
        cont_dic["contract_id"] = booking.contract_id
        cont_dic["created_at"] = booking.created_at.__str__()
        cont_dic["currency"] = booking.currency
        cont_dic["deposit_amount"] = str(booking.deposit_amount)
        cont_dic["ended_at"] = booking.ended_at.__str__()
        cont_dic["insurance_amount"] = str(booking.insurance_amount)
        cont_dic["ip"] = booking.ip
        cont_dic["owner"] = "/api/1.0/user/%s/" % booking.owner.id
        cont_dic["pin"] = booking.pin
        cont_dic["preapproval_key"] = booking.preapproval_key
        cont_dic["preapproval_url"] = settings.PAYPAL_COMMAND % urlencode({'cmd': '_ap-preapproval','preapprovalkey': booking.preapproval_key})
        cont_dic["product"] = "/api/1.0/product/%s/" % booking.product.id
        cont_dic["resource_uri"] = "/api/1.0/product/%s/" % booking.uuid
        cont_dic["started_at"] = booking.started_at.__str__()
        cont_dic["state"] = booking.state
        cont_dic["total_amount"] = str(booking.total_amount)
        cont_dic["uuid"] = str(booking.uuid)
        content = json.dumps(cont_dic)
        return content
        
    def obj_get_list(self, request=None, **kwargs):
        """
        Initiate the list of objects which will be sent to the user
        """
        from datetime import datetime, timedelta
        from dateutil import parser

        if "started_at" in request.GET and "ended_at" in request.GET:
            #print "good place"
            object_list = Booking.objects.all()[:1]
        elif "uuid" in request.GET:
            try:
                object_list = Booking.objects.filter(uuid=request.GET["uuid"])
                if list(object_list)[0].owner != request.user and list(object_list)[0].borrower != request.user:
                    object_list = Booking.objects.none()
                    raise NotFound("The logined user is neither the owner nor the borrower of the booking with the uuid")
                #print object_list.values()[0]
            except ValueError:
                raise NotFound("Invalid resource lookup data provided (mismatched type).")
            
        else:
            object_list = self.get_object_list(request).filter( Q(borrower=request.user) | Q(owner=request.user) )
        return object_list
 
    def dehydrate(self, bundle, request=None):
        """
        Modify the data before sending it to the client
        """
        #print "enter dehydrate"
        from datetime import datetime, timedelta
        from dateutil import parser
        if "started_at" in request.GET and "ended_at" in request.GET:
            #print unquote(request.GET["started_at"])
            #print unquote(request.GET["ended_at"])
            started_at = parser.parse(unquote(request.GET["started_at"]))
            ended_at = parser.parse(unquote(request.GET["ended_at"]))
            bundle.data = {}
            bundle.obj.product = Product.objects.get(id = request.GET["product"].split("/")[-2])
            temp, bundle.data["total_amount"] = Booking.calculate_price(bundle.obj.product, started_at, ended_at)
            bundle.data["owner"] = "/api/1.0/user/%s/" % bundle.obj.product.owner.id
            bundle.data["borrower"] = unquote(request.GET["borrower"])
            bundle.data["product"] = unquote(request.GET["product"])
            bundle.data["started_at"] = parser.parse(unquote(request.GET["started_at"]))
            bundle.data["ended_at"] = parser.parse(unquote(request.GET["ended_at"]))
        #else:
         #   started_at = datetime.now() + timedelta(days=1)
          #  ended_at = started_at + timedelta(days=1)
        return bundle        
        
api_v1 = Api(api_name='1.0')
api_v1.register(CategoryResource())
api_v1.register(ProductResource())
api_v1.register(AddressResource())
api_v1.register(PhoneNumberResource())
api_v1.register(PictureResource())
api_v1.register(PriceResource())
api_v1.register(UserResource())
api_v1.register(BookingResource())
