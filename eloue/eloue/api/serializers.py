
import copy
import base64
from posixpath import basename
from urllib2 import urlparse

import requests

from django.core.files.base import ContentFile
from django.utils.datastructures import SortedDict

from rest_framework import serializers, status

class NullBooleanField(serializers.BooleanField):
    def field_from_native(self, data, files, field_name, into):
        return super(NullBooleanField, self).field_from_native(
            data, files, field_name, into
        )

    def from_native(self, value):
        return value if value is None else super(NullBooleanField, self).from_native(value)

class EncodedImageField(serializers.ImageField):
    def from_native(self, value):
        if type(value) is dict:
            encoding = value.get('encoding', 'base64')
            filename = value.get('filename', '')
            content = value['content']
            if encoding == 'base64':
                content = base64.b64decode(content)
            elif encoding == 'url':
                res = requests.get(content, stream=True)
                if status.is_success(res.status_code):
                    if not filename:
                        filename = basename(urlparse.urlsplit(content)[2])
                    content = res.content
            value = ContentFile(content, name=filename)
        return super(EncodedImageField, self).from_native(value)

class ModelSerializerOptions(serializers.HyperlinkedModelSerializerOptions):
    """
    Meta class options for ModelSerializer
    """
    def __init__(self, meta):
        super(ModelSerializerOptions, self).__init__(meta)
        self.immutable_fields = getattr(meta, 'immutable_fields', ())

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer that deals with model instances and querysets.
    """
    _options_class = ModelSerializerOptions

    def get_fields(self):
        """
        Returns the complete set of fields for the object as a dict.

        This will be the set of any explicitly declared fields,
        plus the set of fields returned by get_default_fields().
        """
        ret = SortedDict()

        # Get the explicitly declared fields
        base_fields = copy.deepcopy(self.base_fields)
        for key, field in base_fields.items():
            ret[key] = field

        # Add in the default fields
        default_fields = self.get_default_fields()
        for key, val in default_fields.items():
            if key not in ret:
                ret[key] = val

        # If 'fields' is specified, use those fields, in that order.
        if self.opts.fields:
            assert isinstance(self.opts.fields, (list, tuple)), '`fields` must be a list or tuple'
            new = SortedDict()
            for key in self.opts.fields:
                new[key] = ret[key]
            ret = new

        # Remove anything in 'exclude'
        if self.opts.exclude:
            assert isinstance(self.opts.exclude, (list, tuple)), '`exclude` must be a list or tuple'
            for key in self.opts.exclude:
                ret.pop(key, None)

        # Mark immutable fields as read-only if there was an object instance provided
        if self.object:
            # Ensure that 'immutable_fields' is an iterable
            assert isinstance(self.opts.immutable_fields, (list, tuple)), '`immutable_fields` must be a list or tuple'

            # Set the `read_only` flag to any fields that have been specified
            # in the `immutable_fields` option
            for field_name in self.opts.immutable_fields:
                assert field_name in ret, (
                    "Non-existant field '%s' specified in `immutable_fields` "
                    "on serializer '%s'." %
                    (field_name, self.__class__.__name__))
                ret[field_name].read_only = True

        for key, field in ret.items():
            field.initialize(parent=self, field_name=key)

        return ret
