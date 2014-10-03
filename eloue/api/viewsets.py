# -*- coding: utf-8 -*-
import itertools

from rest_framework import viewsets, mixins
from eloue.api.permissions import AllowPublicRetrieve

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


class UndeterminedPermissionMixin(object):
    """
    View set that allow permission checker don't make decision (return None).

    If there isn't at least one checker made decision it is assumed that
    access denied.
    """

    def check_permissions(self, request):
        decision_made = False
        for permission in self.get_permissions():
            has_pemission = permission.has_permission(request, self)
            if has_pemission is None:
                continue

            decision_made = True
            if not has_pemission:
                self.permission_denied(request)

        if not decision_made:
            self.permission_denied(request)


class ModelViewSet(
    UndeterminedPermissionMixin,
    Api20ErrorMessagesMixin,
    LocationHeaderMixin,
    viewsets.ModelViewSet):
    pass

class ReadOnlyModelViewSet(
    UndeterminedPermissionMixin,
    Api20ErrorMessagesMixin,
    LocationHeaderMixin,
    viewsets.ReadOnlyModelViewSet):
    pass

class ImmutableModelViewSet(
    UndeterminedPermissionMixin,
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


def allow_anonymous_retrieve(cls):
    """Decorator that add to ViewSet ability of getting objects anonymously."""
    cls.permission_classes = tuple(
        itertools.chain((AllowPublicRetrieve,), cls.permission_classes))
    return cls
