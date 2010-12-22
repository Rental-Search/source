# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site


def site(request):
    try:
        return {'site': Site.objects.get_current()}
    except Site.DoesNotExist:
        return {'site': None}

def debug(request):
    return {'debug': settings.DEBUG}
