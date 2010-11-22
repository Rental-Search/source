# -*- coding: utf-8 -*-
from logbook import Logger

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseBadRequest

from eloue.decorators import secure_required
from eloue.accounts.forms import EmailAuthenticationForm, PatronEditForm
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


def authenticate_headless(request):
    print request.POST
    form = EmailAuthenticationForm(request.POST or None)

    if form.is_valid():
        return HttpResponse()
    elif request.method == "GET":
        return HttpResponse(csrf(request)["csrf_token"]._proxy____func())

    return HttpResponseBadRequest()


@cache_page(900)
def patron_detail(request, slug, patron_id=None, page=None):
    if patron_id:  # This is here to be compatible with the old app
        return redirect_to(request, reverse('patron_detail', args=[slug]))
    form = FacetedSearchForm()
    patron = get_object_or_404(Patron, slug=slug)
    return object_list(request, patron.products.all(), page=page, paginate_by=PAGINATE_PRODUCTS_BY,
        template_name='accounts/patron_detail.html', template_object_name='product', extra_context={'form': form, 'patron': patron})


@login_required
def patron_edit(request):
    form = PatronEditForm(request.POST or None)
    if form.is_valid():
        patron = form.save()
    return direct_to_template(request, 'accounts/patron_edit.html', extra_context={'form': form, 'patron':request.user})


@login_required
def dashboard(request):
    return direct_to_template(request, 'accounts/dashboard.html')


@login_required
def patron_bookings(request, page=None):
    return object_list(request, request.user.bookings.all(), page=page, paginate_by=10, template_name='accounts/patron_bookings.html',
        template_object_name='booking')


@login_required
def patron_rentals(request, page=None):
    return object_list(request, request.user.rentals.all(), page=page, paginate_by=10, template_name='accounts/patron_rentals.html',
        template_object_name='booking')
