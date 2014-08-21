# -*- coding: utf-8 -*-

from rest_framework import viewsets, mixins

class ImmutableModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    """
    A viewset that provides default `create()`, `retrieve()` and `list()` actions.
    """
    pass

class NonEditableModelViewSet(mixins.DestroyModelMixin, ImmutableModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, 'destroy()' and `list()` actions.
    """
    pass
