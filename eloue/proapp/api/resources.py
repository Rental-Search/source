
import datetime

from collections import defaultdict

from django.conf.urls import url
from django.http import Http404
from tastypie.api import Api
from tastypie.resources import Resource
from tastypie.utils import trailing_slash


from eloue.proapp.analytics_api_v3_auth import GoogleAnalyticsSetStats
from eloue.proapp.api.authentication import SessionAuthentication
from eloue.proapp.forms import TimeSeriesForm
from eloue.accounts.models import Patron


def get_time_series(request=None):
	"""Return time series for qsstats"""
	end_date = datetime.date.today()
	start_date = (end_date - datetime.timedelta(days=30))
	interval = 'days'

	if request.GET.get('start_date') or request.GET.get('end_date') or request.GET.get('interval'):
		form = TimeSeriesForm(request.GET)
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


#Google Analytics resources
class PageViewResource(Resource):
	class Meta:
		resource_name = 'pageviews'
		authentication = SessionAuthentication()

	def prepend_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/analytics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_analytics_pageviews'), name="api_get_analytics_pageviews"),
		]

	def get_analytics_pageviews(self, request, **kwargs):
		self.is_authenticated(request)
		self.method_check(request, allowed=['get'])
		self.throttle_check(request)
		
		patron = request.user

		
		data = []
		details = []
		totalResults = 0

		#Time series
		start_date, end_date, interval = get_time_series(request=request)

		#Google Analytics References
		metrics = 'ga:pageviews'
		dimensions = 'ga:pagePath'
		filters = 'ga:pagePathLevel2==/%s/' % patron.slug

		#Google Analytics Query
		partial_data, partial_details, partial_totalResults = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		data += partial_data
		details += partial_details
		totalResults += partial_totalResults


		position = 0

		while (patron.products.all().count() != position):

			products = patron.products.all()[position:][:45]

			#Time series
			start_date, end_date, interval = get_time_series(request=request)

			#Google Analytics References
			metrics = 'ga:pageviews'
			dimensions = 'ga:pagePath'
			filters = '%s' % ",".join(["ga:pagePathLevel4=@-%s/" % (product.pk) for product in products])

			#Google Analytics Query
			partial_data, partial_details, partial_totalResults = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

			data += partial_data
			details += partial_details
			totalResults += partial_totalResults
			position += products.count()


		group_by_data = defaultdict(int)

		for date, total in data:
			group_by_data[date] += total

		
		data = []
		for key in sorted(group_by_data.iterkeys()):
				data.append((key, group_by_data[key]))

		objects = {
			'data': data,
			'details': details,
			'start_date': start_date,
			'end_date': end_date,
			'interval': interval,
			'count': totalResults
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

	def prepend_urls(self):
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
		data, details, totalResults = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details,
			'start_date': start_date,
			'end_date': end_date,
			'interval': interval,
			'count': totalResults
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

	def prepend_urls(self):
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
		data, details, totalResults = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details,
			'start_date': start_date,
			'end_date': end_date,
			'interval': interval,
			'count': totalResults
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

	def prepend_urls(self):
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
		data, details, totalResults = GoogleAnalyticsSetStats(metrics=metrics, dimensions=dimensions, filters=filters).time_serie(start_date, end_date, interval=interval)

		objects = {
			'data': data,
			'details': details,
			'start_date': start_date,
			'end_date': end_date,
			'interval': interval,
			'count': totalResults
		}

		object_list = {
			'objects': objects
		}

		self.log_throttled_access(request)
		return self.create_response(request, object_list)




api_v1 = Api(api_name='1.0')

api_v1.register(PageViewResource())
api_v1.register(RedirectionEventResource())
api_v1.register(PhoneEventResource())
api_v1.register(AddressEventResource())
