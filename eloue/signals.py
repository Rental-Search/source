# -*- coding: utf-8 -*-
from django.conf import settings

def post_save_sites(sender, instance, created, **kwargs):
    instance.sites.add(*settings.DEFAULT_SITES)
