# -*- coding: utf-8 -*-
import hashlib
import hmac
import locale

from decimal import Decimal as D
from urlparse import urlparse, urljoin

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
from django.utils import translation

CAMO_URL = getattr(settings, 'CAMO_URL', 'https://media.e-loue.com/proxy/')
CAMO_KEY = getattr(settings, 'CAMO_KEY')

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


def cache_key(fragment_name, *args):
    hasher = md5_constructor(u':'.join([urlquote(arg) for arg in args]))
    return 'template.cache.%s.%s' % (fragment_name, hasher.hexdigest())


def create_alternative_email(prefix, context, from_email, recipient_list):
    context.update({
        'site': Site.objects.get_current(),
        'protocol': "https" if USE_HTTPS else "http"
    })
    subject = render_to_string("%s_email_subject.txt" % prefix, context)
    text_content = render_to_string("%s_email.txt" % prefix, context)
    html_content = render_to_string("%s_email.html" % prefix, context)
    message = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    message.attach_alternative(html_content, "text/html")
    return message


def generate_camo_url(url):
    parts = urlparse(url)
    parts = {
        'scheme': parts.scheme,
        'hostname': parts.hostname,
        'path': parts.path if not parts.path.startswith('//') else parts.path[1:],
        'params': parts.params
    }
    url = urljoin("%(scheme)s://%(hostname)s" % parts, "%(path)s?%(params)s" % parts)
    digest = hmac.new(CAMO_KEY, url, hashlib.sha1).hexdigest()
    return "%s%s?url=%s" % (CAMO_URL, digest, url)


def currency(value):
    """It totally ignores currency linked with value."""
    old_locale = locale.getlocale()
    if settings.CONVERT_XPF:
        return "%s F" % convert_to_xpf(D(value))
    try:
        new_locale = locale.normalize(translation.to_locale("%s.utf8" % translation.get_language()))
        locale.setlocale(locale.LC_ALL, new_locale)
        return locale.currency(D(value), True, True)
    except (TypeError, locale.Error):
        return D(value)
    finally:
        locale.setlocale(locale.LC_ALL, old_locale)


def convert_to_xpf(value):
    amount = value / D(settings.XPF_EXCHANGE_RATE)
    return amount.quantize(D(".00"))


def convert_from_xpf(value):
    amount = value * D(settings.XPF_EXCHANGE_RATE)
    return amount.quantize(D(".00"))
