# coding=utf-8

from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def eloue_url(value):
    site = settings.DASHBOARD_REDIRECT_DOMAIN
    protocol = 'https' if settings.USE_HTTPS else 'http'
    path = reverse(value)
    return '%s://%s%s' % (protocol, site, path)
