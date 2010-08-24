# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to

from eloue.accounts.models import Patron

@never_cache
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    patron = Patron.objects.activate(activation_key)
    return direct_to_template(request, 'auth/activate.html', extra_context={ 'patron':patron, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS })
