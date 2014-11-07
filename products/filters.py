# coding=utf-8
from django.db.models.query_utils import Q
from rest_framework.filters import BaseFilterBackend


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
