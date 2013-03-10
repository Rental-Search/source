
import qsstats
import datetime

from django.conf.urls.defaults import *
from django.http import Http404
from tastypie import fields
from tastypie.api import Api
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, Resource
from tastypie.utils import trailing_slash


from eloue.proapp.analytics_api_v3_auth import GoogleAnalyticsSetStats
from eloue.proapp.api.authentication import SessionAuthentication
from eloue.proapp.forms import TimeSerieForm
from eloue.products.models import Product, Category, Picture, Price
from eloue.accounts.models import Patron, Address, PhoneNumber, Subscription, CreditCard


def get_time_series(request=None):
	"""Return time series for qsstats"""
	end_date = datetime.date.today()
	start_date = (end_date - datetime.timedelta(days=30))
	interval = 'days'

	if request.GET.get('start_date') or request.GET.get('end_date') or request.GET.get('interval'):
		form = TimeSerieForm(request.GET)
		if form.is_valid():
			start_date = form.cleaned_data['start_date']
			end_date = form.cleaned_data['end_date']
			interval = form.cleaned_data['interval']
		else:
			raise Http404([(k, u'%s' % 
				v[0]) for k, v in form.errors.items()])

	return start_date, end_date, interval


def get_analytics_event_references(event_action, event_label):
	metrics = 'ga:totalEvents'
	dimensions = 'ga:pagePath,ga:eventAction,ga:eventLabel'
	filters = 'ga:eventLabel==%s;ga:eventAction==%s' % (event_label, event_action)

	return metrics, dimensions, filters	

#Products resources
class ProductResource(ModelResource):
	category = fields.ToOneField('eloue.proapp.api.resources.CategoryResource', 'category', related_name='categories', full=True)

	class Meta:
		queryset = Product.objects.all()
		resource_name = 'products/product'
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get', 'post', 'put', 'delete']
		excludes = ['currency', 'payment_type']
		ordering = ['created_at']
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(owner=request.user)

	def obj_create(self, bundle, request=None, **kwargs):
		return super(EnvironmentResource, self).obj_create(bundle, request, owner=request.user)


class CategoryResource(ModelResource):
	parent = fields.ToOneField('eloue.proapp.api.resources.CategoryResource', 'parent', related_name='children', null=True)

	class Meta:
		queryset = Category.objects.all()
		resource_name = 'products/category'
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get']
		excludes = ['tree_id', 'rght', 'lft']
		filtering = {"parent": ('exact',)}
		authentication = SessionAuthentication()


class PictureResource(ModelResource):
	product = fields.ToOneField('eloue.proapp.api.resources.ProductResource', 'product', related_name='pictures')

	class Meta:
		queryset = Picture.objects.all()
		resource_name = 'products/picture'
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get', 'post', 'put', 'delete']
		ordering = ['created_at']
		filtering = {"product": ('exact',)}
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(product__owner=request.user)

	def obj_create(self, bundle, request=None, **kwargs):
		return super(EnvironmentResource, self).obj_create(bundle, request, product__owner=request.user)


class PriceResource(ModelResource):
	product = fields.ToOneField('eloue.proapp.api.resources.ProductResource', 'product', related_name='pictures')

	class Meta:
		queryset = Price.objects.all()
		resource_name = 'products/price'
		list_allowed_methods = ['get', 'post', 'put', 'delete']
		detail_allowed_methods = ['get', 'post', 'put', 'delete']
		filtering = {"product": ('exact',)}
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(product__owner=request.user)

	def obj_create(self, bundle, request=None, **kwargs):
		return super(EnvironmentResource, self).obj_create(bundle, request, product__owner=request.user)


#Accounts resources
class PatronResource(ModelResource):
	class Meta:
		queryset = Patron.objects.all()
		resource_name = 'accounts/patron'
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get', 'post', 'put']
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(pk=request.user.pk)


class AddressResource(ModelResource):
	class Meta:
		queryset = Address.objects.all()
		resource_name = 'accounts/address'
		list_allowed_methods = ['get', 'put', 'delete']
		detail_allowed_methods = ['get', 'post', 'put', 'delete']
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(patron=request.user)


class PhoneNumberResource(ModelResource):
	class Meta:
		queryset = PhoneNumber.objects.all()
		resource_name = 'accounts/phone_number'
		list_allowed_methods = ['get', 'put', 'delete']
		detail_allowed_methods = ['get', 'post', 'put', 'delete']
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(patron=request.user)


class SubscriptionResource(ModelResource):
	class Meta:
		queryset = Subscription.objects.all()
		resource_name = 'accounts/subscription'
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get', 'post', 'put']
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(patron=request.user)


class CreditCardResource(ModelResource):
	class Meta:
		queryset = CreditCard.objects.all()
		resource_name = 'accounts/credit_card'
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get', 'post']
		excludes = ['card_number']
		authentication = SessionAuthentication()

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(holder=request.user)


#Events resources
class PageViewResource(Resource):
	class Meta:
		resource_name = 'pageviews'
		authentication = SessionAuthentication()

	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_pageviews'), name="api_get_analytics_pageviews"),
		]

	def get_analytics_pageviews(self, request, **kwargs):
		self.is_authenticated(request)
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)
		
		patron = request.user
		print patron.products.all()

		#Google Analytics References
		metrics = 'ga:pageviews'
		dimensions = 'ga:pagePath'
		filters = 'ga:pagePathLevel2==/%s/,%s' % (patron.slug, ",".join(["ga:pagePathLevel4=@%s-%s" % (product.slug, product.pk) for product in patron.products.all()])) 

		#Time series
		start_date, end_date, interval = get_time_series(request=request)

		#Google Analytics Query
		data, details = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details
		}

		object_list = {
			'objects': objects
		}

		self.log_throttled_access(request)
		return self.create_response(request, object_list)


class RedirectionEventResource(Resource):
	class Meta:
		resource_name = 'redirection_events'
		authentication = SessionAuthentication()

	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_redirections'), name="api_get_analytics_redirections"),
		]

	def get_analytics_redirections(self, request, **kwargs):
		self.is_authenticated(request)
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)

		patron = request.user

		#Google Analytics References
		metrics, dimensions, filters = get_analytics_event_references(event_action="Redirection", event_label=patron.slug)

		#Time series
		start_date, end_date, interval = get_time_series(request=request)

		#Google Analytics Query
		data, details = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details
		}

		object_list = {
			'objects': objects
		}

		self.log_throttled_access(request)
		return self.create_response(request, object_list)


class PhoneEventResource(Resource):
	class Meta:
		resource_name = 'phone_events'
		authentication = SessionAuthentication()

	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_phones'), name="api_get_analytics_phones"),
		]

	def get_analytics_phones(self, request, **kwargs):
		self.is_authenticated(request)
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)

		patron = request.user

		#Google Analytics References
		metrics, dimensions, filters = get_analytics_event_references(event_action="Phone", event_label=patron.slug)

		#Time series
		start_date, end_date, interval = get_time_series(request=request)

		#Google Analytics Query
		data, details = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details
		}

		object_list = {
			'objects': objects
		}

		self.log_throttled_access(request)
		return self.create_response(request, object_list)


class AddressEventResource(Resource):
	class Meta:
		resource_name = 'address_events'
		authentication = SessionAuthentication()

	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_addresses'), name="api_get_analytics_addresses"),
		]

	def get_analytics_addresses(self, request, **kwargs):
		self.is_authenticated(request)
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)

		patron = request.user

		#Google Analytics References
		metrics, dimensions, filters = get_analytics_event_references(event_action="Address", event_label=patron.slug)

		#Time series
		start_date, end_date, interval = get_time_series(request=request)

		#Google Analytics Query
		data, details = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details
		}

		object_list = {
			'objects': objects
		}

		self.log_throttled_access(request)
		return self.create_response(request, object_list)




api_v1 = Api(api_name='1.0')
api_v1.register(ProductResource())
api_v1.register(CategoryResource())
api_v1.register(PictureResource())
api_v1.register(PriceResource())
api_v1.register(PageViewResource())
api_v1.register(RedirectionEventResource())
api_v1.register(PhoneEventResource())
api_v1.register(AddressEventResource())
api_v1.register(PatronResource())
api_v1.register(AddressResource())
api_v1.register(PhoneNumberResource())
api_v1.register(SubscriptionResource())
api_v1.register(CreditCardResource())
