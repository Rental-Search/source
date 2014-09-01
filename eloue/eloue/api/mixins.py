
from django.core.urlresolvers import reverse

class LocationHeaderMixin(object):
    def get_success_headers(self, data):
        try:
            return {'Location': self.get_location_url()}
        except (TypeError, KeyError):
            return {}

    def get_location_url(self):
        obj = self.object
        return reverse('%s-detail' % obj._meta.model_name, args=(obj.pk,))

class SetOwnerMixin(object):
    owner_field = 'patron'

    def pre_save(self, obj):
        user = self.request.user
        if not user.is_anonymous():
            owner_field = self.owner_field
            if not isinstance(owner_field, basestring):
                owner_field = iter(owner_field).next()
            owner_field_attname = obj._meta.get_field(owner_field).attname
            if not getattr(obj, owner_field_attname):
                setattr(obj, owner_field, user)
        return super(SetOwnerMixin, self).pre_save(obj)
