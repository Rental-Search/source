# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse

from rest_framework.utils.encoders import JSONEncoder, json

def serialize(data, **kwargs):
    return json.dumps(data, cls=JSONEncoder, **kwargs)

class JsonResponse(HttpResponse):
    content_type = 'application/json'

    def __init__(self, content=b'', *args, **kwargs):
        encoding = kwargs.pop('encoding', settings.DEFAULT_CHARSET)
        kwargs.setdefault('content_type', '%s; charset=%s' % (
            self.content_type, encoding
        ))
        data = serialize(content, encoding=encoding)
        super(JsonResponse, self).__init__(data, *args, **kwargs)
