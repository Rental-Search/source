# -*- coding: utf-8 -*-
from __future__ import absolute_import
from urllib import urlencode
import datetime

from suds import WebFault

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.datastructures import MultiValueDict
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.encoding import smart_str
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, TemplateView, View
from django.db.models import Q

from rest_framework.decorators import link, action
from rest_framework.response import Response
from rest_framework import status

import django_filters

from eloue.views import AjaxResponseMixin
from eloue.decorators import ajax_required
from products.forms import SuggestCategoryViewForm

from eloue.api import viewsets, filters, mixins, permissions
from eloue.api.decorators import ignore_filters, list_link, list_action
from eloue.api.exceptions import ValidationException, ServerException, ServerErrorEnum
from eloue.utils import currency
from eloue.decorators import mobify
from eloue.geocoder import GoogleGeocoder
from eloue.views import SearchQuerySetMixin, BreadcrumbsMixin

from rent.models import Booking, Comment
from rent.utils import timesince
from rent.forms import BookingForm

from shipping import helpers
from shipping.models import ShippingPoint
from shipping.serializers import ShippingPointListParamsSerializer, PudoSerializer

from .forms import ProductFacetedSearchForm
from .models import (
    Category, Product, CarProduct, RealEstateProduct
)
from .choices import UNIT, SORT, PRODUCT_TYPE
from .utils import escape_percent_sign
from .search import product_search
from .serializers import get_root_category
from . import serializers, models, filters as product_filters

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 12) # UI v3: changed from 10 to 12
PAGINATE_UNAVAILABILITY_PERIODS_BY = getattr(settings, 'PAGINATE_UNAVAILABILITY_PERIODS_BY', 31)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)
MAX_DISTANCE = 1541


def get_point_and_radius(coords, radius=None):
    """get_point_and_radius(coords, radius=None):
    A helper function which transforms provided coordinates into a gis.geos.Point object and validates radius.

    Input:
    - coords : coordinates of the center of the zone of interest, tuple or list;
               must contain (latitude, longitude) in strict order
    - radius : a radius of the zone of interests, numeric (int or float), or any 'False' value like None, False, empty sequences, etc.

    Output: a (point, radius) tuple where
    - point : gis.geos.Point object made from the input coordinates
    - radius : a validated radius of the zone of interests, numeric (int or float)
    """
    point = Point(*coords)
    radius = min(radius or float('inf'), MAX_DISTANCE)
    return point, radius

def get_last_added_sqs(search_index, location, sort_by_date='-created_at_date'):
    # only objects that are 'good' to be shown
    sqs = search_index.filter(is_good=True)

    # try to find products in the same region
    region_point, region_radius = get_point_and_radius(
        location['region_coords'] or location['coordinates'],
        location['region_radius'] or location['radius']
        )
    last_added = sqs.dwithin('location', region_point, Distance(km=region_radius)
        ).distance('location', region_point
        ).order_by(sort_by_date, SORT.NEAR)

    # if there are no products found in the same region
    if not last_added.count():
        # try to find products in the same country
        try:
            country_point, country_radius = get_point_and_radius(GoogleGeocoder().geocode(location['country'])[1:3])
        except:
            # silently ignore exceptions like country name is missing or incorrect
            pass
        else:
            last_added = sqs.dwithin('location', country_point, Distance(km=country_radius)
                ).distance('location', country_point
                ).order_by(sort_by_date, SORT.NEAR)

    # if there are no products found in the same country
    if not last_added.count():
        # do not filter on location, and return full list sorted by the provided date field only
        last_added = sqs.order_by(sort_by_date)

    return last_added


def last_added(search_index, location, offset=0, limit=PAGINATE_PRODUCTS_BY, sort_by_date='-created_at_date'):
    last_added = get_last_added_sqs(search_index, location, sort_by_date)
    return last_added[offset*limit:(offset+1)*limit]


def get_booking_price_from_form(form):
    product = form.instance.product
    if form.is_valid():
        duration = timesince(form.cleaned_data['started_at'], form.cleaned_data['ended_at'])
        total_price = smart_str(currency(form.cleaned_data['total_amount']))
        price_unit = form.cleaned_data['price_unit']
        quantity = form.cleaned_data['quantity']
        max_available = form.max_available
        if quantity is None and max_available > 0:
            quantity = 1
        response_dict = {
          'duration': duration,
          'total_price': total_price,
          'unit_name': UNIT[price_unit][1],
          'unit_value': smart_str(currency(product.prices.filter(unit=price_unit)[0].amount)),
          'max_available': max_available,
          'quantity': max_available if quantity > max_available else quantity,
        }
        if quantity > max_available:
            response_dict.setdefault('warnings', []).append(_(u'Quantité disponible à cette période: %s') % max_available)
    else:
        max_available = getattr(form, 'max_available', product.quantity)
        try:
            price_unit = product.prices.filter(unit=1)[0]
            response_dict = {
              'unit_name': UNIT[1][1],
              'unit_value': smart_str(currency(price_unit.amount)),
              'max_available': max_available,
              'quantity': 1,
            }
        except:
            response_dict = {}
    return response_dict


# UI v3


class NavbarCategoryMixin(object):
    def get_context_data(self, **kwargs):
        category_list = list(Category.on_site.filter(pk__in=settings.NAVBAR_CATEGORIES))
        index = settings.NAVBAR_CATEGORIES.index
        category_list.sort(key=lambda obj: index(obj.pk))
        context = {
            'category_list': category_list,
        }
        context.update(super(NavbarCategoryMixin, self).get_context_data(**kwargs))
        return context


class HomepageView(NavbarCategoryMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        product_list = last_added(product_search, self.location, limit=8)
        comment_list = Comment.objects.select_related(
            'booking__product__address'
        ).filter(
            booking__product__sites__id=settings.SITE_ID
        ).order_by('-created_at')

        context = {
            'product_list': product_list,
            'comment_list': comment_list,
            'products_on_site': Product.on_site.only('id'),
        }
        context.update(super(HomepageView, self).get_context_data(**kwargs))
        return context

    def get(self, request, *args, **kwargs):
        self.location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        return super(HomepageView, self).get(request, *args, **kwargs)


class CategoryDetailView(NavbarCategoryMixin, BreadcrumbsMixin, DetailView):
    model = Category
    # hardcoded for e-loue
    queryset = Category.on_site.filter(pk__in=settings.NAVBAR_CATEGORIES[:8])
    template_name = 'products/category.jade'

    def get_context_data(self, **kwargs):
        category_slugs = [x.slug for x in self.object.get_descendants(include_self=True)]
        context = {
            'products_on_category': product_search.filter(categories__in=category_slugs),
        }
        context.update(super(CategoryDetailView, self).get_context_data(**kwargs))

        return context


class ProductListView(SearchQuerySetMixin, BreadcrumbsMixin, ListView):
    template_name = 'products/product_list.jade'
    context_object_name = 'product_list'
    paginate_by = PAGINATE_PRODUCTS_BY
    form_class = ProductFacetedSearchForm

    @method_decorator(mobify)
    @method_decorator(vary_on_cookie)
    def dispatch(self, request, urlbits=None, sqs=None, **kwargs):
        self.breadcrumbs = self.get_breadcrumbs(request)
        page = None
        urlbits = filter(None, urlbits.split('/')[::-1]) if urlbits else []
        while urlbits:
            bit = urlbits.pop()
            if bit.startswith(_('par-')): # FIXME: seems like it is not used anymore, needs checking
                try:
                    value = urlbits.pop()
                except IndexError:
                    raise Http404
                if bit.endswith(_('categorie')):
                    item = get_object_or_404(Category, slug=value)
                    is_facet_not_empty = lambda facet: not (
                        facet['facet'] or
                        (facet['label'], facet['value']) in [ ('sort', ''), ('q', '')]
                    )
                    params = MultiValueDict(
                        (facet['label'], [unicode(facet['value']).encode('utf-8')]) for facet in self.breadcrumbs.values() if is_facet_not_empty(facet)
                    )
                    path = item.get_absolute_url()
                    for bit in urlbits:
                        if bit.startswith(_('page')):
                            try:
                                page = urlbits.pop(0)
                                path = '%s/%s/%s' % (path, _(u'page'), page)
                            except IndexError:
                                raise Http404
                    if any([value for key, value in params.iteritems()]):
                        path = '%s?%s' % (path, urlencode(params))
                    return redirect(escape_percent_sign(path))
                else:
                    raise Http404
            elif bit.startswith(_('page')):
                try:
                    page = urlbits.pop()
                except IndexError:
                    raise Http404
            else:
                value = bit
                item = get_object_or_404(Category, slug=value)
                ancestors_slug = item.get_ancertors_slug()
                self.breadcrumbs['categorie'] = {
                    'name': 'categories', 'value': value, 'label': ancestors_slug, 'object': item,
                    'pretty_name': _(u"Catégorie"), 'pretty_value': item.name,
                    'url': item.get_absolute_url(), 'facet': True
                }
        # Django 1.5+ ignore *args and **kwargs in View.dispatch(),
        # and collects "page" only from URLconf and from request.GET
        # which is not our case. Force update self.kwargs here.
        if page:
            self.kwargs.update({'page': page})
        return super(ProductListView, self).dispatch(request, sqs=sqs, **kwargs)

    @method_decorator(cache_page(900)) # TBD: 15 minutes of caching for search results - is it OK?
    def get(self, request, *args, **kwargs):
        form = self.form_class(
            dict((facet['name'], facet['value']) for facet in self.breadcrumbs.values()),
            searchqueryset=self.sqs
        )
        if not form.is_valid():
            raise Http404
        self.sqs, suggestions, top_products = form.search()
        self.form = form
        return super(ProductListView, self).get(request, *args, **kwargs)

    def get_breadcrumbs(self, request):
        breadcrumbs = super(ProductListView, self).get_breadcrumbs(request)
        form = self.form
        breadcrumbs['date_from'] = {'name': 'date_from', 'value': form.cleaned_data.get('date_from', None), 'label': 'date_from', 'facet': False}
        breadcrumbs['date_to'] = {'name': 'date_to', 'value': form.cleaned_data.get('date_to', None), 'label': 'date_to', 'facet': False}
        breadcrumbs['price_from'] = {'name': 'price_from', 'value': form.cleaned_data.get('price_from', None), 'label': 'price_from', 'facet': False}
        breadcrumbs['price_to'] = {'name': 'price_to', 'value': form.cleaned_data.get('price_to', None), 'label': 'price_to', 'facet': False}
        breadcrumbs['categorie'] = {'name': 'categorie', 'value': None, 'label': 'categorie', 'facet': True}
        return breadcrumbs

    def get_context_data(self, **kwargs):
        if settings.FILTER_CATEGORIES:
            category_list = Category.on_site.filter(id__in=settings.FILTER_CATEGORIES)
        else:
            category_list = Category.on_site.filter(
                Q(parent__isnull=True) | ~Q(parent__sites__id=settings.SITE_ID)
            ).exclude(slug='divers')

        context = {
            'category_list': category_list,
            'facets': self.sqs.facet_counts(),
            'form': self.form,
        }
        filter_limits = self.form.filter_limits
        if filter_limits:
            context.update(filter_limits)
        context.update(super(ProductListView, self).get_context_data(**kwargs))

        return context


class ProductDetailView(SearchQuerySetMixin, DetailView):
    model = Product
    template_name = 'products/_base_product_detail.jade'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # check if slug has changed
        product = self.object.object
        if product.slug != kwargs['slug']:
            return redirect(product, permanent=True)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        product = self.object.object
        if not product:
            raise Http404
        product_type = product.name
        comment_qs = Comment.borrowercomments.select_related('booking__borrower', 'booking_product').order_by('-created_at')
        # FIXME: It seems to be that `more_like_this` don't support filtration, but we need only products in response.
        # http://stackoverflow.com/questions/17537787/haystack-more-like-this-ignores-filters
        product_list = []
        chunk_size = 5
        i = 0
        while len(product_list) < 5:
            chunk = self.sqs.more_like_this(product)[i*chunk_size:(i+1)*chunk_size]
            if not chunk:
                break
            product_list.extend(filter(lambda x: x and isinstance(x.object, (Product, CarProduct, RealEstateProduct)), chunk))
            i += 1
        product_list = product_list[:5]

        product_comment_list = comment_qs.filter(booking__product=product)
        owner_comment_list = comment_qs.filter(booking__owner=product.owner)

        context = {
            'properties': product.properties.select_related('property'),
            'product_list': product_list,
            'product_comments': product_comment_list,
            'owner_comments': owner_comment_list,
            'product_type': product_type,
            'product_object': getattr(product, product_type) if product_type != 'product' else product,
            'insurance_available': settings.INSURANCE_AVAILABLE,
            'shipping_enabled': True,
        }
        context.update(super(ProductDetailView, self).get_context_data(**kwargs))
        return context


class PublishItemView(NavbarCategoryMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'publich_item/index.jade'

    def get_context_data(self, **kwargs):
        context = super(PublishItemView, self).get_context_data(**kwargs)
        publish_categories = getattr(settings, 'PUBLISH_CATEGORIES', tuple())
        if publish_categories:
            context['publish_category_list'] = publish_categories
        return context


class LandingPagePublishItemView(PublishItemView):
    template_name = 'landing_pages/publish.jade'


class SuggestCategoryView(AjaxResponseMixin, View):

    @method_decorator(ajax_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # search for products by provided query string
        form = SuggestCategoryViewForm(self.request.GET, searchqueryset=product_search)
        if not form.is_valid():
            return dict(errors=form.errors)

        sqs = form.search()

        # collect categories from product records found
        categories_set = reduce(lambda a, b: a.update(b.categories if b else []) or a, sqs, set())

        qs = Category.on_site.all()
        # we should filter by tree_id first because of SQL query performance benefits
        category = form.cleaned_data['category']
        if category is not None:
            qs = qs.filter(tree_id=category._mpttfield('tree_id'))
        qs = qs.filter(slug__in=categories_set)

        context = dict(categories=[
            [dict(id=c.id, name=c.name) for c in cat.get_ancestors(include_self=True)]
            for cat in qs if cat.is_leaf_node()
        ])
        return context


# REST API 2.0


class CategoryFilterSet(filters.FilterSet):
    parent__isnull = django_filters.Filter(name='parent', lookup_type='isnull')
    is_child_node = filters.MPTTBooleanFilter(lookup_type='is_child_node')
    is_leaf_node = filters.MPTTBooleanFilter(lookup_type='is_leaf_node')
    is_root_node = filters.MPTTBooleanFilter(lookup_type='is_root_node')

    class Meta:
        model = models.Category
        fields = ('parent', 'need_insurance')


class CategoryViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product categories to be viewed or edited.
    """
    permission_classes = (permissions.IsStaffOrReadOnly,)
    queryset = models.Category.on_site.select_related('description__title')
    serializer_class = serializers.CategorySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CategoryFilterSet
    ordering_fields = ('name',)
    public_actions = ('list', 'retrieve', 'ancestors', 'children', 'descendants')
    cache_control = {'max_age': 60*60} # categories are not going to change frequently

    @link()
    def ancestors(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_ancestors(), many=True)
        return Response(serializer.data)

    @link()
    def children(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_children(), many=True)
        return Response(serializer.data)

    @link()
    def descendants(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_descendants(), many=True)
        return Response(serializer.data)


class ProductFilterSet(filters.FilterSet):
    category__isdescendant = filters.MPTTModelFilter(name='categories', lookup_type='descendants', queryset=Category.objects.all())
    category = django_filters.ModelChoiceFilter(name='categories', queryset=Category.objects.all())

    class Meta:
        model = models.Product
        fields = ('deposit_amount', 'currency', 'address', 'is_archived', 'owner', 'created_at', 'quantity')


class ProductOrderingFilter(filters.OrderingFilter):

    def get_ordering(self, request):
        ordering = super(ProductOrderingFilter, self).get_ordering(request)
        if ordering:
            for i, param in enumerate(ordering):
                if 'category' in param:
                    ordering[i] = param.replace('category', 'categories__id')
        return ordering


class ProductViewSet(mixins.OwnerListPublicSearchMixin, mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.on_site.filter(is_archived=False).select_related('carproduct', 'realestateproduct', 'address', 'phone', 'category', 'owner')
    filter_backends = (product_filters.ProductHaystackSearchFilter,
        filters.DjangoFilterBackend, product_filters.HaystackOrderingFilter)
    owner_field = 'owner'
    search_index = product_search
    filter_class = ProductFilterSet
    ordering = '-created_at'
    ordering_fields = ('quantity', 'is_archived', 'category', 'created_at')
    haystack_ordering_fields = ('price', 'average_rate', 'distance')
    public_actions = ('retrieve', 'search', 'is_available',
                      'homepage', 'unavailability_periods')
    paginate_by = PAGINATE_PRODUCTS_BY

    navette = helpers.EloueNavette()

    _object = None

    # FIXME move to viewsets.ModelViewSet ??
    def get_object(self, queryset=None):
        if self._object is None:
            self._object = super(ProductViewSet, self
                    ).get_object(queryset=queryset)
        return self._object

    @link()
    def shipping_price(self, request, *args, **kwargs):
        params = serializers.ShippingPriceParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            product = self.get_object()
            try:
                departure_point = product.departure_point
            except ShippingPoint.DoesNotExist:
                raise ServerException({
                    'code': ServerErrorEnum.OTHER_ERROR[0],
                    'description': ServerErrorEnum.OTHER_ERROR[1],
                    'detail': _(u'Departure point not specified')
                })
            result = serializers.ShippingPriceSerializer(
                data=self.navette.get_shipping_price(departure_point.site_id, params['arrival_point_id']))
            if result.is_valid():
                return Response(result.data)

    @link()
    @ignore_filters([filters.DjangoFilterBackend])
    def shipping_points(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            departure_point = product.departure_point
        except ShippingPoint.DoesNotExist:
            raise ServerException({
                'code': ServerErrorEnum.OTHER_ERROR[0],
                'description': ServerErrorEnum.OTHER_ERROR[1],
                'detail': _(u'Departure point not specified')
            })

        params = ShippingPointListParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            lat = params['lat']
            lng = params['lng']
            if lat is None or lng is None:
                lat, lng = helpers.get_position(params['address'])
                if not all((lat, lng)):
                    return Response([])
            shipping_points = self.navette.get_shipping_points(lat, lng, params['search_type'])
            for shipping_point in shipping_points:
                # FIXME: could there be a depot without site_id?
                if 'site_id' in shipping_point:
                    try:
                        price = self.navette.get_shipping_price(departure_point.site_id, shipping_point['site_id'])
                    except WebFault:
                        shipping_points.remove(shipping_point)
                    else:
                        price['price'] *= 2
                        shipping_point.update(price)
                        # shipping_point.update({'price': 3.99})
            result = PudoSerializer(data=shipping_points, many=True)
            if result.is_valid():
                return Response(result.data)
        return Response([])

    @link()
    @ignore_filters([product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend])
    def is_available(self, request, *args, **kwargs):
        obj = self.get_object()

        form = BookingForm(data=request.GET, instance=Booking(product=obj))
        res = get_booking_price_from_form(form)

        # add errors if the form is invalid
        if not form.is_valid():
            res['errors'] = form.errors
            return Response(res, status=400)

        return Response(res)

    @link()
    @ignore_filters([product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend])
    def unavailability(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = serializers.ListUnavailabilityPeriodSerializer(
                        data=request.QUERY_PARAMS,
                        context={'request': request},
                        instance=product)
        if not serializer.is_valid():
            raise ValidationException(serializer.errors)

        return Response(serializer.data)

    @link()
    @ignore_filters([product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend])
    def unavailability_periods(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = serializers.MixUnavailabilityPeriodSerializer(
                context={'request': request, 'product': product},
                data=[request.QUERY_PARAMS,],
                many=True
        )

        if not serializer.is_valid():
            raise ValidationException(serializer.errors)

        self.object_list = serializer.context['object']
        self.paginate_by = PAGINATE_UNAVAILABILITY_PERIODS_BY
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = serializers.MixUnavailabilityPeriodPaginatedSerializer(
                    page,
                    context={'request': request, 'product': product}
            )

        return Response(serializer.data)

    @list_link()
    @ignore_filters([filters.HaystackSearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter])
    def homepage(self, request, *args, **kwargs):
        # get product ids from the search index
        location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        self.object_list = get_last_added_sqs(self.search_index, location)

        # we need to transform Haystack's SearchQuerySet to Django's QuerySet
        # TODO: it may be better to provide a custom Serializer which would support both
        def sqs_to_qs(sqs):
            pks = [obj.pk for obj in sqs]
            qs = self.get_queryset().filter(id__in=pks)
            return qs

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            page.object_list = sqs_to_qs(page.object_list)
            serializer = self.get_pagination_serializer(page)
        else:
            self.object_list = sqs_to_qs(self.object_list)
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)

    @link()
    def stats(self, request, *args, **kwargs):
        return Response(self.get_object().stats)

    @link()
    def absolute_url(self, request, *args, **kwargs):
        obj = self.get_object()
        return Response(dict(url=obj.get_absolute_url()))

    @cached_property
    def _category_from_native(self):
        return self.serializer_class().fields['category'].from_native

    def get_serializer_class(self):
        data = getattr(self, '_post_data', None)
        if data is not None:
            delattr(self, '_post_data')
            category = data.get('category', None)
            if category is not None:
                category = get_root_category(
                        self._category_from_native(category))
            if category == PRODUCT_TYPE.CAR or 'brand' in data:
                # we have CarProduct here
                return serializers.CarProductSerializer
            elif category == PRODUCT_TYPE.REALESTATE or 'private_life' in data:
                # we have RealEstateProduct here
                return serializers.RealEstateProductSerializer
        instance = getattr(self, 'object', None)
        if instance is not None:
            if hasattr(instance, 'carproduct'):
                # we have CarProduct here
                return serializers.CarProductSerializer
            elif hasattr(instance, 'realestateproduct'):
                # we have RealEstateProduct here
                return serializers.RealEstateProductSerializer
        return super(ProductViewSet, self).get_serializer_class()

    def get_serializer(self, instance=None, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        
        We should use different Seializer classes for instances of
        Product, CarProduct and RealEstateProduct models
        """
        if instance is not None:
            if hasattr(instance, 'carproduct'):
                # we have CarProduct here
                self.object = instance = instance.carproduct
            elif hasattr(instance, 'realestateproduct'):
                # we have RealEstateProduct here
                self.object = instance = instance.realestateproduct
        return super(ProductViewSet, self).get_serializer(instance=instance, **kwargs)

    def create(self, request, *args, **kwargs):
        self._post_data = request.DATA
        return super(ProductViewSet, self).create(request, *args, **kwargs)

    def get_location_url(self):
        return reverse('product-detail', args=(self.object.pk,))


class PriceViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product prices to be viewed or edited.
    """
    model = models.Price
    serializer_class = serializers.PriceSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'product__owner'
    filter_fields = ('product', 'unit')
    ordering_fields = ('name', 'amount')
    public_actions = ('retrieve',)


class UnavailabilityPeriodViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product unavailability periods to be viewed or edited.
    """
    model = models.UnavailabilityPeriod
    serializer_class = serializers.UnavailabilityPeriodSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, )
    owner_field = 'product__owner'
    filter_fields = ('product', )
    public_actions = ('list', 'retrieve')


class PictureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product images to be viewed or edited.
    """
    model = models.Picture
    serializer_class = serializers.PictureSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'product__owner'
    filter_fields = ('product', 'created_at')
    ordering_fields = ('created_at',)
    public_actions = ('retrieve',)


class CuriosityViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product curiosities to be viewed or edited.
    """
    queryset = models.Curiosity.on_site.all()
    serializer_class = serializers.CuriositySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('product',) # TODO: 'city', 'price')
    # TODO: ordering_fields = ('price',)
    public_actions = ('retrieve', 'list', )


class MessageThreadFilterSet(filters.FilterSet):
    participant = filters.MultiFieldFilter(name=('sender', 'recipient'))
    empty = django_filters.BooleanFilter(name='last_message__isnull')

    class Meta:
        model = models.MessageThread
        fields = ('sender', 'recipient', 'product')


class SetMessageOwnerMixin(mixins.SetOwnerMixin):
    def pre_save(self, obj):
        # set owner only for new messages threads
        if obj.id:
            return super(mixins.SetOwnerMixin, self).pre_save(obj)
        return super(SetMessageOwnerMixin, self).pre_save(obj)


class MessageThreadViewSet(SetMessageOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows message threads to be viewed or edited.
    """
    model = models.MessageThread
    queryset = models.MessageThread.objects.prefetch_related('messages').select_related('last_message')
    serializer_class = serializers.MessageThreadSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.RelatedOrderingFilter)
    owner_field = ('sender', 'recipient')
    filter_class = MessageThreadFilterSet
    ordering_fields = ('last_message__sent_at', 'last_message__read_at', 'last_message__replied_at')

    @link()
    @ignore_filters([filters.DjangoFilterBackend])
    def seen(self, request, *args, **kwargs):
        thread = self.get_object()
        serializer = self.get_serializer()
        seen = serializer.transform_seen(thread, thread.id)
        return Response({'seen': seen})


class ProductRelatedMessageViewSet(SetMessageOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows product related messages to be viewed or edited.
    """
    model = models.ProductRelatedMessage
    serializer_class = serializers.ProductRelatedMessageSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = ('sender', 'recipient')
    filter_fields = ('thread', 'sender', 'recipient', 'offer')
    ordering_fields = ('sent_at',)

    def pre_save(self, obj):
        if not obj.subject and obj.thread:
            obj.subject = obj.thread.subject
        return super(ProductRelatedMessageViewSet, self).pre_save(obj)

    @action(methods=['put'])
    @ignore_filters([filters.DjangoFilterBackend])
    def seen(self, request, *args, **kwargs):
        message = self.get_object()
        if not message.read_at and message.recipient.id == request.user.id:
            message.read_at = datetime.datetime.now()
            message.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_action(methods=['put'], url_path='seen')
    @ignore_filters([filters.DjangoFilterBackend])
    def seen_many(self, request, *args, **kwargs):
        messages_ids = request.DATA.get('messages', [])
        if not isinstance(messages_ids, (list, tuple)):
            messages_ids = [messages_ids, ]

        self.get_queryset().filter(
            recipient=request.user,
            read_at__isnull=True,
            id__in=messages_ids).update(
            read_at=datetime.datetime.now())

        return Response(status=status.HTTP_204_NO_CONTENT)
