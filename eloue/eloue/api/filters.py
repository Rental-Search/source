
from rest_framework import filters

DjangoFilterBackend = filters.DjangoFilterBackend

class OwnerFilter(filters.BaseFilterBackend):
    """
    Filter that allows users to see their own objects only.
    """
    owner_field = 'patron'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if user.is_staff or user.is_superuser:
            return queryset
        elif user.is_anonymous:
            return queryset.none()
        owner_field = getattr(view, 'owner_field', self.owner_field)
        return queryset.filter(**{owner_field: user})

class HaystackSearchFilter(filters.BaseFilterBackend):
    # The URL query parameter used for the search.
    search_param = filters.SearchFilter.search_param

    def get_query_string(self, request):
        """
        Search string is set by a ?search=... query parameter,
        where the parameter name is defined in SearchFilter.search_param
        """
        query_string = request.QUERY_PARAMS.get(self.search_param, '')
        return query_string

    def filter_queryset(self, request, queryset, view):
        search_index = getattr(view, 'search_index', None)
        query_string = self.get_query_string(request)

        if search_index is not None and query_string:
            sqs = search_index.auto_query(query_string)
            queryset = queryset.filter(pk__in=[int(pk) for pk in sqs])

        return queryset
