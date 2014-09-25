# -*- coding: utf-8 -*-

from rest_framework import viewsets, mixins

from .mixins import LocationHeaderMixin


def api_2_0_error_messages(cls):
    """
    Decorate view set with ability to return error messages according to
    api 2.0 spec requirements.
    """

    class Api20ErrorMessagesViewSet(cls):
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
            context = super(Api20ErrorMessagesViewSet, self).get_serializer_context()
            context['suppress_exception'] = not self.validation_exception_expected
            return context

        def initialize_request(self, request, *args, **kwargs):
            """Enable exception raising on validation errors."""
            self.validation_exception_expected = True
            return super(Api20ErrorMessagesViewSet, self).initialize_request(
                request, *args, **kwargs)

        def finalize_response(self, request, response, *args, **kwargs):
            """Disable exception raising on validation errors.

            It is necessary for correct work of Django REST Framework GUI.
            """
            self.validation_exception_expected = False
            return super(Api20ErrorMessagesViewSet, self).finalize_response(
                request, response, *args, **kwargs)

    return Api20ErrorMessagesViewSet


@api_2_0_error_messages
class ModelViewSet(LocationHeaderMixin, viewsets.ModelViewSet):
    pass

ReadOnlyModelViewSet = api_2_0_error_messages(viewsets.ReadOnlyModelViewSet)


@api_2_0_error_messages
class ImmutableModelViewSet(
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
