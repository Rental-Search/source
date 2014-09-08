# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from .filters import OwnerFilter
from .permissions import OwnerPermissions

class LocationHeaderMixin(object):
    def get_success_headers(self, data):
        try:
            return {'Location': self.get_location_url()}
        except (TypeError, KeyError):
            return {}

    def get_location_url(self):
        obj = self.object
        return reverse('%s-detail' % obj._meta.model_name, args=(obj.pk,))

class OwnerListMixin(object):
    owner_filter_class = OwnerFilter

    def paginate_queryset(self, queryset, page_size=None):
        if self.owner_filter_class not in self.get_filter_backends():
            self.object_list = self.owner_filter_class().filter_queryset(self.request, queryset, self)
        return super(OwnerListMixin, self).paginate_queryset(self.object_list, page_size=page_size)

class SetOwnerMixin(OwnerListMixin):
    owner_field = 'patron'
    permission_classes = (OwnerPermissions,)

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
