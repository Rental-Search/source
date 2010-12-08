# -*- coding: utf-8 -*-
from django.utils.html import strip_spaces_between_tags as compress_html
from django.utils.encoding import DjangoUnicodeDecodeError


class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            try:
                response.content = compress_html(response.content)
            except DjangoUnicodeDecodeError:
                pass
        return response
    
