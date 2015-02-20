# coding=utf-8

import operator
from django.db.models.query_utils import Q
from rest_framework.filters import BaseFilterBackend

from products.forms import APIProductFacetedSearchForm
from eloue.api.filters import HaystackSearchFilter


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


class ProductHaystackSearchFilter(HaystackSearchFilter):
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
                # TODO Try to get model_name
                idx = 'idx(array[%s], products_product.id)' % ', '.join(
                        _id for _id in pks)

                queryset = queryset.filter(pk__in=pks).extra(
                        select={'idx': idx}, order_by = ['idx'])
                # mark the view has search results
                # FIXME: should be a better (more safe) way to do this
                view._haystack_filter = True

        self.remove_haystack_ordering(request, view)

        return queryset

    def remove_haystack_ordering(self, request, view):
        ordering = request.QUERY_PARAMS.get('ordering')
        if ordering in view.haystack_ordering_fields:
            request._request.GET = request._request.GET.copy()
            request.QUERY_PARAMS.pop('ordering')
