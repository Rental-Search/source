# -*- coding: utf-8 -*-
import operator
import re

from django.db.models import Q, ForeignKey, F
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import RelatedObject
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django import forms

from rest_framework import filters
from mptt.fields import TreeNodeMultipleChoiceField

import django_filters


DjangoFilterBackend = filters.DjangoFilterBackend

class OrderingFilter(filters.OrderingFilter):
    def remove_invalid_fields(self, queryset, ordering, view):
        valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)

        # preapre a dict to map resource attributes to model fields
        trans = {
            field_name: field.source or field_name
            for field_name, field in view.get_serializer().fields.items()
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

class RelatedOrderingFilter(OrderingFilter):
    """
    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation
    """
    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field, parent_model, direct, m2m = \
                model._meta.get_field_by_name(components[0])

            # reverse relation
            if isinstance(field, RelatedObject):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.rel and len(components) == 2:
                return self.is_valid_field(field.rel.to, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, ordering, view):
        return [
            term for term in ordering
            if self.is_valid_field(queryset.model, term.lstrip('-'))
        ]

class OwnerFilter(filters.BaseFilterBackend):
    """
    Filter that allows users to see their own objects only.
    """
    owner_field = 'patron'

    def filter_queryset(self, request, queryset, view):
        # restrictions for public mode are set with permission, not filters
        if view.public_mode:
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

class HaystackSearchFilter(filters.BaseFilterBackend):
    """
    Uses Haystack to search by requested terms, and filters Django QuerySet
    by found records, if any.
    """
    # The URL query parameter used for the search.
    search_param = filters.SearchFilter.search_param

    def get_query_string(self, request):
        """
        Search string is set by a ?search=... query parameter,
        where the parameter name is defined in SearchFilter.search_param
        """
        query_string = request.QUERY_PARAMS.get(self.search_param, '')
        return query_string

    def get_search_queryset(self, view):
        """
        Returns SearchQuerySet instance to be used for full-text search and
        filtering.
        """
        sqs = getattr(view, 'search_index', None)
        return sqs

    def filter_search_queryset(self, request, sqs):
        """
        Applies supported filters to the SearchQuerySet.
        """
        if sqs:
            query_string = self.get_query_string(request)
            if query_string:
                sqs = sqs.auto_query(query_string)
                return sqs

    def filter_queryset(self, request, queryset, view):
        view._haystack_filter = False

        sqs = self.get_search_queryset(view)
        if sqs is not None:
            filtered_sqs = self.filter_search_queryset(request, sqs)
            # sqs was filtered
            if filtered_sqs not in (None, sqs):
                # FIXME should be better way to limit results
                pks = [obj.pk for obj in filtered_sqs[:200]]
                queryset = queryset.filter(pk__in=pks)
                # mark the view has search results
                # FIXME: should be a better (more safe) way to do this
                view._haystack_filter = True

        return queryset


MULTI_VALUE_FIELD_SPLIT_RE = re.compile(r'([-_\d\w]+)')

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
            res = MULTI_VALUE_FIELD_SPLIT_RE.findall(smart_unicode(value))
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

class MPTTFilterMixin(object):
    def filter(self, qs, value):
        filter_func = getattr(self, 'get_{}'.format(self.lookup_type))
        if not filter_func:
            return qs
        qs = filter_func(qs, value)
        if self.distinct:
            qs = qs.distinct()
        return qs

class MPTTBooleanFilter(MPTTFilterMixin, django_filters.Filter):
    field_class = forms.NullBooleanField

    def get_is_root_node(self, qs, value):
        opts = qs.model._mptt_meta
        return (qs.filter if value else qs.exclude)(**{opts.parent_attr: None})

    def get_is_child_node(self, qs, value):
        return self.get_is_root_node(qs, not value)

    def get_is_leaf_node(self, qs, value):
        opts = qs.model._mptt_meta
        return (qs.filter if value else qs.exclude)(**{opts.left_attr: (F(opts.right_attr) - 1)})

class MPTTModelFilter(MPTTFilterMixin, django_filters.ModelMultipleChoiceFilter):
    field_class = TreeNodeMultipleChoiceField

    def filter(self, qs, value):
        if not value:
            return qs
        return super(MPTTModelFilter, self).filter(qs, value)

    def join_parts(self, *args):
        return  '__'.join((self.name,) + args if self.name else args)

    def get_descendants(self, qs, value):
        or_queries = []
        for category in value:
            if category.is_leaf_node():
                continue
            opts = category._mptt_meta
            or_queries.append(Q(**{
                # MPTT descendants
                self.join_parts(opts.tree_id_attr): getattr(category, opts.tree_id_attr),
                self.join_parts(opts.left_attr, 'gt'): getattr(category, opts.left_attr),
                self.join_parts(opts.right_attr, 'lt'): getattr(category, opts.right_attr),
            }))
        if not or_queries:
            return qs.none()
        return qs.filter(reduce(operator.or_, or_queries))

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
