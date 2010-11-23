# -*- coding: utf-8 -*-
from logbook import Logger

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list

from eloue.decorators import secure_required
from eloue.accounts.forms import EmailAuthenticationForm, PatronEditForm, PatronPaypalForm
from eloue.accounts.models import Patron
from eloue.accounts.wizard import AuthenticationWizard

from eloue.products.forms import FacetedSearchForm
from eloue.rent.models import Booking

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

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
    return object_list(request, patron.products.all(), page=page, paginate_by=PAGINATE_PRODUCTS_BY,
        template_name='accounts/patron_detail.html', template_object_name='product', extra_context={'form': form, 'patron': patron})


@login_required
def patron_edit(request):
    form = PatronEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        patron = form.save()
    return direct_to_template(request, 'accounts/patron_edit.html', extra_context={'form': form, 'patron': request.user})


@login_required
def patron_edit_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, _(u"Votre mot de passe à bien été modifié"))
    return direct_to_template(request, 'accounts/patron_password.html', extra_context={'form': form, 'patron': request.user})


@login_required
def patron_paypal(request):
    form = PatronPaypalForm(request.POST or None,
        initial={'paypal_email': request.user.email}, instance=request.user)
    redirect_path = request.REQUEST.get('next', '')
    if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
        redirect_path = reverse('dashboard')
    if form.is_valid():
        patron = form.save()
        protocol = 'https' if USE_HTTPS else 'http'
        domain = Site.objects.get_current().domain
        return_url = "%s://%s%s?paypal=true" % (protocol, domain, redirect_path)
        paypal_redirect = patron.create_account(return_url=return_url)
        if paypal_redirect:
            return redirect_to(request, paypal_redirect)
        messages.error(request, _(u"Nous n'avons pas pu créer votre compte paypal"))
    return direct_to_template(request, 'accounts/patron_paypal.html', extra_context={'form': form, 'next': redirect_path})


@login_required
def dashboard(request):
    return direct_to_template(request, 'accounts/dashboard.html')


@login_required
def owner_booking(request, page=None):
    queryset = request.user.bookings.exclude(state__in=[Booking.STATE.CLOSED, Booking.STATE.REJECTED])
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/owner_booking.html',
        template_object_name='booking')


@login_required
def owner_history(request, page=None):
    queryset = request.user.bookings.filter(state__in=[Booking.STATE.CLOSED, Booking.STATE.REJECTED])
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/owner_history.html',
        template_object_name='booking')


@login_required
def owner_product(request, page=None):
    queryset = request.user.products.all()
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/owner_product.html',
        template_object_name='product')


@login_required
def borrower_booking(request, page=None):
    queryset = request.user.rentals.exclude(state__in=[Booking.STATE.CLOSED, Booking.STATE.REJECTED])
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/borrower_booking.html',
        template_object_name='booking')


@login_required
def borrower_history(request, page=None):
    queryset = request.user.rentals.filter(state__in=[Booking.STATE.CLOSED, Booking.STATE.REJECTED])
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/borrower_history.html',
        template_object_name='booking')
