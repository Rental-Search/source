# -*- coding: utf-8 -*-

from rest_framework import viewsets, mixins
from eloue.api.mixins import IgnoreFilterMixin
from .mixins import LocationHeaderMixin, ErrorMixin, PermissionMixin, CacheControlMixin


class SimpleViewSet(
    PermissionMixin,
    ErrorMixin,
    viewsets.ViewSet
):
    pass


class ModelViewSet(
    IgnoreFilterMixin,
    CacheControlMixin,
    PermissionMixin,
    ErrorMixin,
    LocationHeaderMixin,
    viewsets.ModelViewSet
):
    pass


class ReadOnlyModelViewSet(
    IgnoreFilterMixin,
    CacheControlMixin,
    PermissionMixin,
    ErrorMixin,
    LocationHeaderMixin,
    viewsets.ReadOnlyModelViewSet
):
    pass


class ImmutableModelViewSet(
    IgnoreFilterMixin,
    CacheControlMixin,
    PermissionMixin,
    ErrorMixin,
    LocationHeaderMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset that provides default `create()`, `retrieve()` and `list()`,
    but misses 'destroy()', `update()` and `partial_update()` actions.
    """
    pass

class NonEditableModelViewSet(mixins.DestroyModelMixin, ImmutableModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, 'destroy()' and
    `list()`, but misses `update()` and `partial_update()` actions.
    """
    pass

class NonDeletableModelViewSet(mixins.UpdateModelMixin, ImmutableModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()` and `list()`, but misses 'destroy()' action.
    """
    pass
