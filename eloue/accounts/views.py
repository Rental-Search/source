# -*- coding: utf-8 -*-
from logbook import Logger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list

from eloue.decorators import validate_ipn, secure_required
from eloue.accounts.forms import CreateAccountIPNForm, EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.accounts.wizard import AuthenticationWizard

from eloue.products.forms import FacetedSearchForm

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)

log = Logger('eloue.accounts')


@never_cache
@secure_required
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower()  # Normalize before trying anything with it.
    is_actived = Patron.objects.activate(activation_key)
    return direct_to_template(request, 'accounts/activate.html', extra_context={'is_actived': is_actived, 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS})


@never_cache
@secure_required
def authenticate(request, *args, **kwargs):
    wizard = AuthenticationWizard([EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@cache_page(900)
def patron_detail(request, slug, patron_id=None, page=None):
    if patron_id:  # This is here to be compatible with the old app
        return redirect_to(request, reverse('patron_detail', args=[slug]))
    form = FacetedSearchForm()
    patron = get_object_or_404(Patron, slug=slug)
    return object_list(request, patron.products.all(), page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name='accounts/patron_detail.html', template_object_name='product', extra_context={'form': form, 'patron': patron})


@require_POST
@csrf_exempt
@validate_ipn
def create_account_ipn(request):
    form = CreateAccountIPNForm(request.POST)
    if form.is_valid():
        patron = Patron.objects.get(account_key=form.cleaned_data['account_key'])
    return HttpResponse()
