# -*- coding: utf-8 -*-

from rest_framework import viewsets, mixins

from .mixins import LocationHeaderMixin


class Api20ErrorMessagesMixin(object):
    """
    View set with ability to return error messages according to
    api 2.0 spec requirements.
    """

    validation_exception_expected = True

    def get_serializer_context(self):
        """
        Add to serializer context flag designated whether exception on
        validation errors must be raised.
        """
        context = super(Api20ErrorMessagesMixin, self).get_serializer_context()
        context['suppress_exception'] = not self.validation_exception_expected
        return context

    def initialize_request(self, request, *args, **kwargs):
        """Enable exception raising on validation errors."""
        self.validation_exception_expected = True
        return super(Api20ErrorMessagesMixin, self).initialize_request(
            request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        """Disable exception raising on validation errors.

        It is necessary for correct work of Django REST Framework GUI.
        """
        self.validation_exception_expected = False
        return super(Api20ErrorMessagesMixin, self).finalize_response(
            request, response, *args, **kwargs)

class ModelViewSet(Api20ErrorMessagesMixin, LocationHeaderMixin, viewsets.ModelViewSet):
    pass

class ReadOnlyModelViewSet(Api20ErrorMessagesMixin, LocationHeaderMixin, viewsets.ReadOnlyModelViewSet):
    pass

class ImmutableModelViewSet(
    Api20ErrorMessagesMixin,
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
