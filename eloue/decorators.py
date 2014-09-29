# -*- coding: utf-8 -*-
import re

from httplib2 import Http
from functools import wraps, partial

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import translation
from django.utils.translation import ugettext as _
from django.core.cache import get_cache, cache as default_cache

from eloue.utils import cache_key

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)
USE_PAYPAL_SANDBOX = getattr(settings, 'USE_PAYPAL_SANDBOX', False)
VALIDATE_IPN = getattr(settings, 'VALIDATE_IPN', True)

if USE_PAYPAL_SANDBOX:
    endpoint = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_notify-validate&%s"
else:
    endpoint = "https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate&%s"


MOBILE = getattr(settings, 'MOBILE', False)
MOBILE_REDIRECT_BASE = getattr(settings, 'MOBILE_REDIRECT_BASE', 'https://m.e-loue.com')
RE_MOBILE = re.compile(r"(iphone|ipod|lg|htc|vodafone|netfront|samsung|symbianos|blackberry|android|palm|windows\s+ce|opera\s+mobi|opera\s+mini)", re.I)
RE_DESKTOP = re.compile(r"(windows|linux|os\s+[x9]|solaris|bsd|ipad)", re.I)
RE_BOT = re.compile(r"(spider|crawl|slurp|bot|google|yahoo|msn)", re.I)


def validate_ipn(view_func):
    """Decorator makes sure ipn is coming from Paypal."""
    def _wrapped_view_func(request, *args, **kwargs):
        if VALIDATE_IPN:
            response, content = Http().request(endpoint % request.body)
            if not content == 'VERIFIED':
                return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if USE_HTTPS:
                site = Site.objects.get_current()
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


def get_user_agent(request):
    # Some mobile browsers put the User-Agent in a HTTP-X header
    return request.META.get('HTTP_X_OPERAMINI_PHONE_UA') or \
           request.META.get('HTTP_X_SKYFIRE_PHONE') or \
           request.META.get('HTTP_USER_AGENT', '')


def is_mobile(user_agent):
    """Anything that looks like a phone is a phone."""
    return bool(RE_MOBILE.search(user_agent))


def mobify(view_func=None):
    def wrapper(request, *args, **kwargs):
        user_agent = get_user_agent(request)
        if not MOBILE and is_mobile(user_agent):
            return HttpResponsePermanentRedirect("%s%s" % (MOBILE_REDIRECT_BASE, request.get_full_path()))
        else:
            return view_func(request, *args, **kwargs)
    return wrapper


def cached(timeout=None, cache=None, key_prefix=None, key_func=None, **cache_kwargs):
    if timeout is not None:
        cache_kwargs['timeout'] = timeout
    make_key = partial(key_func or cache_key, key_prefix or Site.objects.get_current().domain)
    cache = default_cache if cache is None else get_cache(cache)
    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            key = make_key(func.__name__)
            value = cache.get(key)
            if value is None:
                value = func(*func_args, **func_kwargs)
                cache.set(key, value, **cache_kwargs)
            return value
        return wrapper
    return decorator


def split_args_int(f):
    @wraps(f)
    def wrapper(value, args):
        if isinstance(args, basestring):
            args = map(int, args.split(':'))
            return f(value, *args)
        return f(value, int(args))
    return wrapper


def split_args_dict(f):
    @wraps(f)
    def wrapper(value, args={}):
        if isinstance(args, basestring):
            args = dict(keyval.split('=') for keyval in args.split(','))
        return f(value, **args)
    return wrapper


def ajax_required(f):
    """
    Decorator makes sure the request is coming from JavaScript.
    """
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest(_('AJAX request is required.'))
        return f(request, *args, **kwargs)
    return wrapper
