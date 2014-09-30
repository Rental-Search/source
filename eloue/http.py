# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse

from rest_framework.utils.encoders import JSONEncoder, json

def serialize(data):
    return json.dumps(data, cls=JSONEncoder)

class JsonResponse(HttpResponse):
    def __init__(self, content=b'', *args, **kwargs):
        kwargs['content_type'] = "%s; charset=%s" % (
            kwargs.pop('content_type', 'application/json'),
            kwargs.pop('charset', settings.DEFAULT_CHARSET)
        )
        super(JsonResponse, self).__init__(serialize(content), *args, **kwargs)
