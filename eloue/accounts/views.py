# -*- coding: utf-8 -*-
from logbook import Logger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_detail

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.accounts.wizard import AuthenticationWizard

log = Logger('eloue.accounts')


@never_cache
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    is_actived = Patron.objects.activate(activation_key)
    return direct_to_template(request, 'accounts/activate.html', extra_context={ 'is_actived':is_actived, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS })


@cache_page(900)
def patron_detail(request, slug, patron_id=None):
    if patron_id: # This is here to be compatible with the old app
        return redirect_to(request, reverse('patron_detail', args=[slug]))
    else:
        return object_detail(request, queryset=Patron.objects.all(), slug=slug, template_object_name='patron')


@never_cache
def authenticate(request, *args, **kwargs):
    wizard = AuthenticationWizard([EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)
