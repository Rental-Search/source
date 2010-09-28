# -*- coding: utf-8 -*-
from httplib2 import Http

from django.conf import settings
from django.db import connection
from django.http import HttpResponseForbidden

if settings.USE_PAYPAL_SANDBOX:
    endpoint = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_notify-validate&%s"
else:
    endpoint = "https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate&%s"

def validate_ipn(view_func):
    """Decorator makes sure ipn is coming from Paypal."""
    def _wrapped_view_func(request, *args, **kwargs):
        if getattr(settings, 'VALIDATE_IPN', True):
            response, content = Http().request(endpoint % request.raw_post_data)
            if not content == 'VERIFIED':
                return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def incr_sequence(field, sequence_name):
    def wrapper(func):
        def inner_wrapper(self, *args, **kwargs):
            if not getattr(self, field):
                cursor = connection.cursor()
                cursor.execute("SELECT nextval(%s)", [sequence_name])
                row = cursor.fetchone()
                setattr(self, field, row[0])
            return func(self, *args, **kwargs)
        return inner_wrapper
    return wrapper
