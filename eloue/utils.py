# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote

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
