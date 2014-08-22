
import operator
import re

from django.db.models import Q, ForeignKey
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django import forms

from rest_framework import filters
from mptt.fields import TreeNodeChoiceField
import django_filters

DjangoFilterBackend = filters.DjangoFilterBackend

class OrderingFilter(filters.OrderingFilter):
    def remove_invalid_fields(self, queryset, ordering, view):
        valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)

        serializer_class = getattr(view, 'serializer_class', None)
        if serializer_class is None:
            msg = ("Cannot use %s on a view which does not have either a "
                   "'serializer_class' or 'ordering_fields' attribute.")
            raise ImproperlyConfigured(msg % self.__class__.__name__)

        # preapre a dict to map resource attributes to model fields
        trans = {
            field_name: field.source or field_name
            for field_name, field in serializer_class().fields.items()
            if not getattr(field, 'write_only', False) and (valid_fields == '__all__' or (field.source or field_name) in valid_fields)
        }

        # validate provided ordering list and replace resource attributes with corresponding model fields
        ordering = [
            minus + trans[field]
            for term in ordering
            for minus, field in (('-' if term.startswith('-') else '', term.lstrip('-')),)
            if field in trans
        ]

        return ordering

class OwnerFilter(filters.BaseFilterBackend):
    """
    Filter that allows users to see their own objects only.
    """
    owner_field = 'patron'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if user.is_anonymous():
            return queryset.none()
        elif user.is_staff or user.is_superuser:
            return queryset
        owner_field = getattr(view, 'owner_field', self.owner_field)
        if isinstance(owner_field, basestring):
            queryset = queryset.filter(**{owner_field: user.pk})
        else:
            or_queries = [Q(**{owner_field: user.pk})
                          for owner_field in owner_field]
            queryset = queryset.filter(reduce(operator.or_, or_queries))
        return queryset

class StaffEditableFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return queryset if request.method == 'get' or user.is_staff else queryset.none()

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
            pks = [obj.pk for obj in sqs]
            if pks:
                queryset = queryset.filter(pk__in=pks)

        return queryset

class MultiValueFormField(forms.CharField):
    default_error_messages = {
        'invalid': _(u'Enter valid primary keys separated by commas.'),
        'invalid_value_type': _(u'This value must be a list, a string or None.'),
    }

    def to_python(self, value):
        """Normalize data to a list of strings."""
        if not value:
            return None
        elif isinstance(value, basestring):
            res = re.findall(r'([\d\w]+)', smart_unicode(value), re.U)
            if value and not res:
                raise ValidationError(self.error_messages['invalid'])
            return res
        elif isinstance(value, list):
            return value
        raise ValidationError(self.error_messages['invalid_value_type'])

class MultiValueForeignKeyFilter(django_filters.Filter):
    field_class = MultiValueFormField

    def filter(self, qs, value):
        if value:
            value = (value, 'in') if len(value) > 1 else value[0]
        return super(MultiValueForeignKeyFilter, self).filter(qs, value)

class MPTTFilter(django_filters.ModelChoiceFilter):
    field_class = TreeNodeChoiceField

    def filter(self, qs, value):
        if not value:
            return qs.none()
        name = self.name
        opts = value._mptt_meta
        qs = qs.filter(**{
            # MPTT descendants
            '__'.join([name, opts.tree_id_attr]): getattr(value, opts.tree_id_attr),
            '__'.join([name, opts.left_attr, 'gt']): getattr(value, opts.left_attr),
            '__'.join([name, opts.right_attr, 'lt']): getattr(value, opts.right_attr),
            })
        if self.distinct:
            qs = qs.distinct()
        return qs

class MultiFieldFilter(django_filters.Filter):
    def __init__(self, op=None, **kwargs):
        super(MultiFieldFilter, self).__init__(**kwargs)
        self.op = operator.or_ if op is None else op

    def filter(self, qs, value):
        if not value:
            return qs.none()
        or_queries = [Q(**{field: value}) for field in self.name]
        qs = qs.filter(reduce(self.op, or_queries))
        return qs

class FilterSet(django_filters.FilterSet):
    filter_overrides = {
        ForeignKey: {
            'filter_class': MultiValueForeignKeyFilter,
        },
    }
