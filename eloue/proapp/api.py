
import qsstats
import datetime

from django.conf.urls.defaults import *
from tastypie.api import Api
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, Resource
from tastypie.utils import trailing_slash
from django.http import Http404

from eloue.proapp.analytics_api_v3_auth import GoogleAnalyticsSetStats
from eloue.proapp.forms import TimeSerieForm
from eloue.products.models import Product
from eloue.accounts.models import Patron



def get_time_series(request=None):
	"""Return time series for qsstats"""
	end_date = datetime.datetime.now()
	start_date = (end_date - datetime.timedelta(days=30))
	interval = 'days'

	if request.GET.get('start_date') or request.GET.get('end_date') or request.GET.get('interval'):
		form = TimeSerieForm(request.GET)
		if form.is_valid():
			start_date = form.cleaned_data['start_date']
			end_date = form.cleaned_data['end_date']
			interval =form.cleaned_data['interval']
		else:
			raise Http404([(k, u'%s' % 
				v[0]) for k, v in form.errors.items()])

	return start_date, end_date, interval


class UserAuthorization(Authorization):
	def apply_limits(self, request, object_list):
		if request and hasattr(request, 'user'):
			return object_list.filter(owner=request.user)
		

class ProductResource(ModelResource):
	class Meta:
		queryset = Product.objects.all()
		resource_name = 'products/product'
		excludes = ['currency', 'payment_type']
		ordering = ['created_at']
		authorization = UserAuthorization()


class PageViewResource(Resource):
	class Meta:
		resource_name = 'pageviews'

	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_pageviews'), name="api_get_analytics_pageviews"),
		]

	def get_analytics_pageviews(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)

		patron = Patron.objects.get(slug='deguizland')

		#Google Analytics References
		metrics = 'ga:pageviews'
		dimensions = 'ga:pagePath'
		filters = 'ga:pagePathLevel2==/%s/,%s' % (patron.slug, ",".join(["ga:pagePathLevel4=@%s" % product.pk for product in patron.products.all()])) 

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


class RedirectionResource(Resource):
	class Meta:
		resource_name = 'redirections'

	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_redirections'), name="api_get_analytics_redirections"),
		]

	def get_analytics_redirections(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)

		patron = Patron.objects.get(slug='deguizland')

		#Google Analytics References
		metrics = 'ga:totalEvents'
		dimensions = 'ga:pagePath,ga:eventAction,ga:eventLabel'
		filters = 'ga:eventLabel==%s' % patron.slug

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
api_v1.register(PageViewResource())
api_v1.register(RedirectionResource())