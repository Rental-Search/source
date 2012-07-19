# -*- coding: utf-8 -*-
import hashlib
import hmac
import locale
import os

from decimal import ROUND_UP, ROUND_DOWN, Decimal as D
from urlparse import urlparse, urljoin

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
from django.utils import translation
import django.forms as forms

CAMO_URL = getattr(settings, 'CAMO_URL', 'https://media.e-loue.com/proxy/')
CAMO_KEY = getattr(settings, 'CAMO_KEY')

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


def form_errors_append(form, field_name, message):
    '''
    Add an ValidationError to a field (instead of __all__) during Form.clean():

    class MyForm(forms.Form):
        def clean(self):
            value_a=self.cleaned_data['value_a']
            value_b=self.cleaned_data['value_b']
            if value_a==... and value_b==...:
                formutils.errors_append(self, 'value_a', u'Value A must be ... if value B is ...')
            return self.cleaned_data
    '''
    assert form.fields.has_key(field_name), field_name
    error_list=form.errors.get(field_name)
    
    if error_list is None:
        error_list=forms.util.ErrorList()
        form.errors[field_name]=error_list
    elif error_list[-1]==message: #FIXME, unicode isn't comparable with str, message in error list cannot work so only two messages are allowed
        return 
    error_list.append(message)


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
        return "%s XPF" % D(value)
    try:
        new_locale = locale.normalize(translation.to_locale("%s.utf8" % translation.get_language()))
        locale.setlocale(locale.LC_ALL, new_locale)
        return locale.currency(D(value), True, True)
    except (TypeError, locale.Error):
        return D(value)
    finally:
        locale.setlocale(locale.LC_ALL, old_locale)


def convert_from_xpf(value):
    amount = value * D(settings.XPF_EXCHANGE_RATE)
    return amount.quantize(D("0.00"), rounding=ROUND_UP)

def convert_to_xpf(value):
    amount = value / D(settings.XPF_EXCHANGE_RATE)
    return amount.quantize(D("0.00"), rounding=ROUND_UP)

def cache_to(instance, path, specname, extension):
    filepath, basename = os.path.split(path)
    filename = os.path.splitext(basename)[0]
    new_name = '{0}_{1}{2}'.format(specname, filename, extension)
    return os.path.join(os.path.join('media', filepath), new_name)



