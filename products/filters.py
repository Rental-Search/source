# coding=utf-8

import operator
from django.db.models.query_utils import Q
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings

from products.forms import APIProductFacetedSearchForm
from eloue.api.filters import HaystackSearchFilter, OrderingFilter


class ProductAvailabilityFilter(BaseFilterBackend):
    """
    Filter that allows to see only products available for order.
    """
    def filter_queryset(self, request, queryset, view):
        products = queryset.clone().filter(
            booking__state__in=["pending", "ongoing"],
            booking__ended_at__gte='started_at',
            booking__started_at__lte='ended_at'
        ).annotate(

        )

        # restrictions for public mode are set with permission, not filters
        public_actions = getattr(view, 'public_actions', None)
        if public_actions and view.action in public_actions:
            return queryset

        user = request.user

        # restrictions for anonymous users are set with permission, not filters
        if user.is_anonymous() or user.is_staff or user.is_superuser:
            return queryset

        owner_field = getattr(view, 'owner_field', self.owner_field)
        if isinstance(owner_field, basestring):
            queryset = queryset.filter(**{owner_field: user.pk})
        else:
            or_queries = [Q(**{owner_field: user.pk})
                          for owner_field in owner_field]
            queryset = queryset.filter(reduce(operator.or_, or_queries))

        return queryset


class HaystackFilterMixin(object):
    haystack_ordering_param = api_settings.ORDERING_PARAM

    def is_haystack_ordering(self, request, view):
        # TODO DRF Ordering is set by a comma delimited ?ordering=... query parameter.
        ordering = request.QUERY_PARAMS.get(self.haystack_ordering_param, '')
        ordering_field = ordering.lstrip('-')
        valid_haystack_ordering = getattr(view, 'haystack_ordering_fields', [])

        return ordering_field in valid_haystack_ordering


class ProductHaystackSearchFilter(HaystackFilterMixin, HaystackSearchFilter):
    """
    Uses additional set of filters when searching for products.
    """
    def filter_search_queryset(self, request, sqs):
        form = APIProductFacetedSearchForm(request.QUERY_PARAMS,
                                           searchqueryset=sqs)
        return form.search()


    def filter_queryset(self, request, queryset, view):
        view._haystack_filter = False

        sqs = self.get_search_queryset(view)
        if sqs is not None:
            filtered_sqs = self.filter_search_queryset(request, sqs)
            # sqs was filtered
            if filtered_sqs not in (None, sqs):
                # FIXME should be better way to limit results
                pks = [obj.pk for obj in filtered_sqs[:200]]

                if self.is_haystack_ordering(request, view):
                    db_table = view.serializer_class.Meta.model._meta.db_table
                    idx = 'idx(array[%s], %s.id)' % (', '.join(
                            _id for _id in pks), db_table)

                    queryset = queryset.filter(pk__in=pks).extra(
                            select={'idx': idx}, order_by=['idx'])
                else:
                    queryset = queryset.filter(pk__in=pks)

                # mark the view has search results
                # FIXME: should be a better (more safe) way to do this
                view._haystack_filter = True

        return queryset


class HaystackOrderingFilter(HaystackFilterMixin, OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        # queryset is already ordered by sqs
        if self.is_haystack_ordering(request, view):
            return queryset

        return super(HaystackOrderingFilter, self).filter_queryset(
            request, queryset, view)
