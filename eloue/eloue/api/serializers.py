
import base64
from posixpath import basename
from urllib2 import urlparse

import requests

from django.core.files.base import ContentFile

from rest_framework.serializers import BooleanField, ImageField

class NullBooleanField(BooleanField):
    def field_from_native(self, data, files, field_name, into):
        return super(BooleanField, self).field_from_native(
            data, files, field_name, into
        )

    def from_native(self, value):
        return value if value is None else super(NullBooleanField, self).from_native(value)

class EncodedImageField(ImageField):
    def from_native(self, value):
        if type(value) is dict:
            encoding = value.get('encoding', 'base64')
            filename = value.get('filename', '')
            content = value['content']
            if encoding == 'base64':
                content = base64.b64decode(content)
            elif encoding == 'url':
                res = requests.get(content, stream=True)
                if res.status_code == 200:
                    if not filename:
                        filename = basename(urlparse.urlsplit(content)[2])
                    content = res.content
            value = ContentFile(content, name=filename)
        return super(ImageField, self).from_native(value)
