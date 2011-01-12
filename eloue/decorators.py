# -*- coding: utf-8 -*-
from httplib2 import Http

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden
from django.utils import translation

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)
USE_PAYPAL_SANDBOX = getattr(settings, 'USE_PAYPAL_SANDBOX', False)
VALIDATE_IPN = getattr(settings, 'VALIDATE_IPN', True)

if USE_PAYPAL_SANDBOX:
    endpoint = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_notify-validate&%s"
else:
    endpoint = "https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate&%s"


def validate_ipn(view_func):
    """Decorator makes sure ipn is coming from Paypal."""
    def _wrapped_view_func(request, *args, **kwargs):
        if VALIDATE_IPN:
            response, content = Http().request(endpoint % request.raw_post_data)
            if not content == 'VERIFIED':
                return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if USE_HTTPS:
                site = Site.objects.get(domain="www.e-loue.com")
                secure_url = "https://%s%s" % (site.domain, request.path)
                return HttpResponsePermanentRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def ownership_required(model, object_key='object_id', ownership=None):
    def wrapper(view_func):
        def inner_wrapper(request, *args, **kwargs):
            user = request.user
            grant = False
            object_id = kwargs.get(object_key, None)
            if object_id:
                names = [(rel.get_accessor_name(), rel.field.name) for rel in user._meta.get_all_related_objects() if rel.model == model]
                if ownership:
                    names = filter(lambda name: name[1] in ownership, names)
                names = map(lambda name: getattr(user, name[0]).filter(pk=object_id).exists(), names)
                if names:
                    grant = any(names)
            if not grant:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return inner_wrapper
    return wrapper

def activate_language(method):
    def _wrapped_method(*args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        return_value = method(*args, **options)
        translation.deactivate()
        return return_value
    return _wrapped_method
