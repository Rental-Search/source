# -*- coding: utf-8 -*-
from __future__ import absolute_import
from decimal import Decimal as D
import re
import inspect

from django import forms
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm
from haystack.utils.geo import Distance, Point
from mptt.forms import TreeNodeChoiceField

from eloue.geocoder import GoogleGeocoder

from .fields import FacetField
from .models import Product, Category
from .choices import SORT, SORT_SEARCH_RESULT

    
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class FilteredSearchMixin(object):
    def get_filters(self):
        return filter(lambda x: x[0].startswith('sqs_filter_'),
                      inspect.getmembers(self, inspect.ismethod))

    def filter_search_queryset(self, sqs, search_params):
        if sqs:
            for _, _filter in self.get_filters():
                sqs = _filter(sqs, search_params)

        return sqs

    def search(self):
        sqs = self.searchqueryset
        if self.is_valid():
            sqs = self.filter_search_queryset(sqs, self.cleaned_data)
        return sqs


class FilteredProductSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'x9 inb search-box-q', 'tabindex': '1', 'placeholder': _(u'Que voulez-vous louer ?')}))
    l = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'x9 inb', 'tabindex': '2', 'placeholder': _(u'Où voulez-vous louer?')}))
    r = forms.DecimalField(required=False, min_value=1, widget=forms.TextInput(attrs={'class': 'ins'}))
    renter = forms.CharField(required=False)
    date_from = forms.DateTimeField(required=False)
    date_to = forms.DateTimeField(required=False)

    filter_limits = {}
    _max_range = _point = None

    def clean_r(self):
        location = self.cleaned_data.get('l', None)
        radius = self.cleaned_data.get('r', None)
        if location not in EMPTY_VALUES and radius in EMPTY_VALUES:
            geocoder = GoogleGeocoder()
            departement = geocoder.get_departement(location)
            if departement:
                name, coordinates, radius = geocoder.geocode(
                                            departement['long_name'])
            else:
                name, coordinates, radius = geocoder.geocode(location)

        if radius in EMPTY_VALUES:
            radius = DEFAULT_RADIUS
        return radius

    def clean_l(self):
        location = self.cleaned_data.get('l', None)
        if location:
            location = re.sub('^[0-9]* +(.*)', r'\1', location)
        return location

    def sqs_filter_q(self, sqs, search_params):
        query_string = search_params.get('q', None)
        if query_string:
            sqs = sqs.auto_query(query_string)
        return sqs

    def sqs_filter_l(self, sqs, search_params):
        location = search_params.get('l', None)
        if location:
            point, self.max_range = self._get_location(location)
            if point:
                sqs = sqs.dwithin(
                    'locations', point, Distance(
                        km=search_params.get('r', self.max_range))
                )
        return sqs

    # r is used with l only.  
    def sqs_filter_r(self, sqs, search_params):
        return sqs

    def sqs_filter_renter(self, sqs, search_params):
        status = search_params.get('renter')
        if status == "particuliers":
            sqs = sqs.filter(pro_owner=False)
        elif status == "professionnels":
            sqs = sqs.filter(pro_owner=True)
        return sqs

    def sqs_filter_date_from(self, sqs, search_params):
        date_from = search_params.get('date_from', None)
        date_to = search_params.get('date_to', None)
        if all((date_from, date_to)):
            range_query = 'NOT starts_unavailable_exact:[{0} TO {1}] AND NOT ends_unavailable_exact:[{0} TO {1}]'
            sqs = sqs.raw_search(range_query.format(date_from.strftime('%F'), date_to.strftime('%F')))
        return sqs

    def sqs_filter_date_to(self, sqs, search_params):
        return sqs

    def _get_location(self, location):
        if not all((self._point, self._max_range)):
            _, coords, radius = GoogleGeocoder().geocode(location)
            self._max_range = radius or DEFAULT_RADIUS
            if all(coords):
                self._point = Point(coords)
        return (self._point, self._max_range)


class FilteredProductPriceSearchForm(FilteredProductSearchForm):
    # Price slider step is 1, so we can't restrict price with minimum value to be 0.01
    price_from = forms.DecimalField(decimal_places=2, max_digits=10, min_value=D('0.00'), required=False)
    price_to = forms.DecimalField(decimal_places=2, max_digits=10, min_value=D('0.00'), required=False)

    def clean_price_from(self):
        price_from = self.cleaned_data.get('price_from', None)
        if price_from is None:
            return
        price_to = self.cleaned_data.get('price_to', None)
        if (price_to is not None and price_from is not None and
            price_from > price_to
        ):
            return
        return price_from

    def clean_price_to(self):
        price_to = self.cleaned_data.get('price_to', None)
        if price_to is None:
            return
        price_from = self.cleaned_data.get('price_from', None)
        if (price_to is not None and price_from is not None and
            price_to < price_from
        ):
            return
        return price_to

    def sqs_filter_price_from(self, sqs, search_params):
        price_from = search_params.get('price_from', None)
        if price_from:
            sqs = sqs.filter(price__gte=price_from)
        return sqs

    def sqs_filter_price_to(self, sqs, search_params):
        price_to = search_params.get('price_to', None)
        if price_to:
            sqs = sqs.filter(price__lte=price_to)
        return sqs


class FacetedSearchForm(FilteredSearchMixin, FilteredProductSearchForm):
    sort = forms.ChoiceField(required=False, choices=SORT, widget=forms.HiddenInput())
    price = FacetField(label=_(u"Prix"), pretty_name=_("par-prix"), required=False)
    categories = FacetField(label=_(u"Catégorie"), pretty_name=_("par-categorie"), required=False, widget=forms.HiddenInput())

    def sqs_filter_q(self, sqs, search_params):
        query_string = search_params.get('q', None)
        self.suggestions = suggestions = None
        if query_string:
            sqs = sqs.auto_query(query_string)
            suggestions = sqs.spelling_suggestion()
            if suggestions:
                suggestions = re.sub('AND\s*', '', suggestions)
                suggestions = re.sub('[\(\)]+', '', suggestions)
                suggestions = re.sub('django_ct:[a-zA-Z\.]*', '', suggestions)
                suggestions = suggestions.strip()
            if suggestions == query_string:
                suggestions = None

            self.suggestions = suggestions
        return sqs

    def sqs_filter_sort(self, sqs, search_params):
        sort = search_params.get('sort')
        if sort:
            sqs = sqs.order_by(sort)
        else:
            sqs = sqs.order_by(SORT.RECENT)
        return sqs

    def unspecified_sqs_filters(self, sqs, search_params):
        exclude_keys = [k.replace('sqs_filter_', '') for
                        k, v in self.get_filters()]

        for key, value in search_params.iteritems():
            if value and key not in exclude_keys:
                sqs = sqs.narrow("%s_exact:%s" % (key, value))
        return sqs 

    def search(self):
        if self.is_valid():
            sqs = self.searchqueryset
            self.suggestions = None

            prices = [price[0] for price in sqs.facet_counts(
                        ).get('fields', {}).get('price', [])]
            if prices:
                self.filter_limits.update({
                    'price_min': min(prices),
                    'price_max': max(prices),
                })

            sqs = self.filter_search_queryset(
                    self.searchqueryset, self.cleaned_data)

            if self.load_all:
                sqs = sqs.load_all()

            sqs = self.unspecified_sqs_filters(
                    sqs, self.cleaned_data)

            return sqs, self.suggestions, None
        else:
            return self.searchqueryset, None, None


class ProductFacetedSearchForm(FacetedSearchForm, FilteredProductPriceSearchForm):
    pass


class APIProductFacetedSearchForm(FilteredSearchMixin,
                                  FilteredProductPriceSearchForm):
    ordering = forms.ChoiceField(required=False, choices=SORT_SEARCH_RESULT,
            widget=forms.HiddenInput())


    def sqs_filter_ordering(self, sqs, search_params):
        ordering = search_params.get('ordering')

        # This filter in valid only for search result!
        if search_params.get('q') and ordering:
            # TODO In DRF Ordering is set by a comma delimited ?ordering=... query parameter.
            # custom rules for ordering by distance
            if ordering == SORT.NEAR:
                location = search_params.get('l', None)
                if location:
                    point, _ = self._get_location(location)
                    if point:
                        sqs = sqs.distance('location', point).order_by(ordering)
            else:
                sqs = sqs.order_by(ordering)

        return sqs


class SuggestCategoryViewForm(SearchForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all(), required=False)


# Django Admin : see admin.py


class ProductAdminForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label="Choisissez une catégorie", level_indicator=u'--')
    
    class Meta:
        model = Product
