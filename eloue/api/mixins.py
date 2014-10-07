# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from .filters import OwnerFilter
from .permissions import IsOwnerOrReadOnly

class LocationHeaderMixin(object):
    def get_success_headers(self, data):
        try:
            return {'Location': self.get_location_url()}
        except (TypeError, KeyError):
            return {}

    def get_location_url(self):
        obj = self.object
        return reverse('%s-detail' % obj._meta.model_name, args=(obj.pk,))

class ErrorMixin(object):
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
        context = super(ErrorMixin, self).get_serializer_context()
        context['suppress_exception'] = not self.validation_exception_expected
        return context

    def initialize_request(self, request, *args, **kwargs):
        """
        Enable exception raising on validation errors.
        """
        self.validation_exception_expected = True
        return super(ErrorMixin, self).initialize_request(
            request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Disable exception raising on validation errors.

        It is necessary for correct work of Django REST Framework GUI.
        """
        self.validation_exception_expected = False
        return super(ErrorMixin, self).finalize_response(
            request, response, *args, **kwargs)

class PermissionMixin(object):
    """
    View set that allow permission checker to pass making a decision (return None).

    If there was not at least one positive decision it is assumed that
    access is denied.
    """
    def check_permissions(self, request):
        permissions = []
        for permission in self.get_permissions():
            has_pemission = permission.has_permission(request, self)
            permissions.append(has_pemission)
            # check if decision has been passed
            if has_pemission is None:
                continue
            # deny access if forbidden
            if not has_pemission:
                self.permission_denied(request)

        # if iteration has finished, and there were no permission exceptions,
        # rise one if there were no positive decisions made (all checkers have returned None)
        if permissions and not any(permissions):
            self.permission_denied(request)

    def get_serializer_context(self):
        """
        Add to serializer context flag designated whether exception on
        validation errors must be raised.
        """
        context = super(PermissionMixin, self).get_serializer_context()
        context['creation'] = (self.action == 'create')
        return context

class OwnerListMixin(object):
    owner_filter_class = OwnerFilter

    def paginate_queryset(self, queryset, page_size=None):
        if self.owner_filter_class not in self.get_filter_backends():
            self.object_list = self.owner_filter_class().filter_queryset(self.request, queryset, self)
        return super(OwnerListMixin, self).paginate_queryset(self.object_list, page_size=page_size)

class OwnerListPublicSearchMixin(OwnerListMixin):
    owner_filter_class = OwnerFilter

    def paginate_queryset(self, queryset, page_size=None):
        if getattr(self, '_haystack_filter', False):
            # we should not filter out records by owner if there are search results
            return super(OwnerListMixin, self).paginate_queryset(self.object_list, page_size=page_size)
        return super(OwnerListPublicSearchMixin, self).paginate_queryset(self.object_list, page_size=page_size)

class SetOwnerMixin(OwnerListMixin):
    owner_field = 'patron'
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.

        The currently authenticated user will be set as the default value for
        the serializer's 'owner_field'. This will allow optional providing of
        values for such fields from the client side.
        """
        serializer = super(SetOwnerMixin, self).get_serializer(*args, **kwargs)
        user = self.request.user
        if not user.is_anonymous():
            owner_field = getattr(self, 'owner_field', None)
            if owner_field:
                if not isinstance(owner_field, basestring):
                    owner_field = iter(owner_field).next()
                owner_field = serializer.fields[owner_field]
                owner_field.default = owner_field.to_native(user)
        return serializer

    def pre_save(self, obj):
        user = self.request.user
        if not user.is_anonymous():
            owner_field = getattr(self, 'owner_field', None)
            if owner_field:
                if not isinstance(owner_field, basestring):
                    owner_field = iter(owner_field).next()
                owner_field_attname = obj._meta.get_field(owner_field).attname
                if not (user.is_staff and getattr(obj, owner_field_attname)):
                    setattr(obj, owner_field, user)
        return super(SetOwnerMixin, self).pre_save(obj)
