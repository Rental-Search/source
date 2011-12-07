# -*- coding: utf-8 -*-
import smtplib
import socket
from logbook import Logger

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, BadHeaderError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login
from oauth_provider.models import Token
from django.shortcuts import redirect

from eloue.decorators import secure_required, mobify
from eloue.accounts.forms import EmailAuthenticationForm, PatronEditForm, PatronPaypalForm, PatronPasswordChangeForm, ContactForm, PatronSetPasswordForm, FacebookForm
from eloue.accounts.models import Patron, FacebookSession
from eloue.accounts.wizard import AuthenticationWizard

from eloue.products.forms import FacetedSearchForm
from eloue.rent.models import Booking
import time


PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

log = Logger('eloue.accounts')


@never_cache
@secure_required
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower()  # Normalize before trying anything with it.
    is_actived = Patron.objects.activate(activation_key)
    return direct_to_template(request, 'accounts/activate.html', extra_context={'is_actived': is_actived,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS})


@never_cache
@secure_required
def authenticate(request, *args, **kwargs):
    if request.user.is_anonymous():
        wizard = AuthenticationWizard([EmailAuthenticationForm])
        return wizard(request, *args, **kwargs)
    else:
        redirect_path = request.GET.get('next', '')
        if redirect_path:
            return redirect(redirect_path)
        else:
            return redirect(settings.LOGIN_REDIRECT_URL)


@never_cache
def authenticate_headless(request):
    form = EmailAuthenticationForm(request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return HttpResponse()
    return HttpResponse(csrf(request)["csrf_token"]._proxy____func())


@never_cache
def oauth_authorize(request, *args, **kwargs):
    return HttpResponse(csrf(request)["csrf_token"]._proxy____func())


@never_cache
def oauth_callback(request, *args, **kwargs):
    token = Token.objects.get(key=kwargs['oauth_token'])
    return HttpResponse(token.verifier)

@never_cache
@login_required
def associate_facebook(request):
    try:
        request.user.facebooksession
    except FacebookSession.DoesNotExist:
        form = FacebookForm(request.POST or None)
        form.user = request.user
        if form.is_valid():
            return redirect('associate_facebook')
        return direct_to_template(request, 'accounts/associate_facebook.html', {'form': form})
    else:
        return direct_to_template(
            request, 'accounts/associated_facebook.html', 
            {'me': request.user.facebooksession.uid}
        )

@cache_page(900)
def patron_detail(request, slug, patron_id=None, page=None):
    if patron_id:  # This is here to be compatible with the old app
        patron = get_object_or_404(Patron.on_site, pk=patron_id)
        return redirect_to(request, patron.get_absolute_url(), permanent=True)
    form = FacetedSearchForm()
    patron = get_object_or_404(Patron.on_site, slug=slug)
    return object_list(request, patron.products.all(), page=page, paginate_by=PAGINATE_PRODUCTS_BY,
        template_name='accounts/patron_detail.html', template_object_name='product', extra_context={'form': form, 'patron': patron})


@login_required
def patron_edit(request, *args, **kwargs):
    paypal = request.GET.get('paypal', False)
    redirect_path = request.REQUEST.get('next', '')
    patron = request.user

    patron_dict = model_to_dict(patron)
    
    form = PatronEditForm(request.POST or patron_dict, request.FILES or None, instance=patron)
    if form.is_valid():
        patron = form.save()
        if paypal:
            is_valid = patron.is_valid
            is_confirmed = patron.is_confirmed
            if patron.is_valid and patron.is_confirmed:
                protocol = 'https' if USE_HTTPS else 'http'
                domain = Site.objects.get_current().domain
                if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
                    redirect_path = reverse('dashboard')
                return_url = "%s://%s%s?paypal=true" % (protocol, domain, redirect_path)
                messages.success(request, _(u"Vos informations ont bien été modifiées et votre compte paypal est valide"))    
                return redirect_to(request, return_url)
            else:
                if not is_valid:
                    messages.error(request, _(u"Votre Paypal compte est invalide, veuillez modifier votre nom ou prénom ou email paypal"))
                if not is_confirmed:
                    messages.error(request,  _(u"Vérifiez que vous avez bien répondu à l'email d'activation de Paypal"))
        elif request.POST:
            messages.success(request, _(u"Vos informations ont bien été modifiées")) 
    patron = Patron.objects.get(pk=request.user.pk)
    return direct_to_template(request, 'accounts/patron_edit.html', extra_context={'form': form, 'patron': patron})


@login_required
def patron_edit_password(request):
    
    form = PatronPasswordChangeForm(request.user, request.POST or None) \
      if request.user.has_usable_password() \
      else PatronSetPasswordForm(request.user, request.POST or None) 
    
    if form.is_valid():
        form.save()
        messages.success(request, _(u"Votre mot de passe à bien été modifié"))
    return direct_to_template(request, 'accounts/patron_password.html', extra_context={'form': form, 'patron': request.user})


@login_required
def patron_paypal(request):
    form = PatronPaypalForm(request.POST or None,
        initial={'paypal_email': request.user.email}, instance=request.user)
    redirect_path = request.REQUEST.get('next', '')
    booking_id = redirect_path.split("/")[-2]
    from eloue.rent.models import Booking
    booking = Booking.objects.get(uuid=booking_id)
    if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
        redirect_path = reverse('dashboard')
    if form.is_valid():
        
        patron = form.save()
        protocol = 'https' if USE_HTTPS else 'http'
        domain = Site.objects.get_current().domain
        return_url = "%s://%s%s?paypal=true" % (protocol, domain, redirect_path)
        profile_edit_url = "%s://%s%s?next=%s&paypal=true"% (protocol, domain, reverse('patron_edit'), redirect_path)
        
        if form.paypal_exists:
            is_valid = patron.is_valid
            is_confirmed = patron.is_confirmed
            if is_valid and is_confirmed:
                messages.success(request, _(u"Votre compte paypal est valide"))
                return redirect_to(request, return_url)
            else:
                if not is_valid:
                    messages.error(request, _(u"Votre Paypal compte est invalide, veuillez modifier votre nom ou prénom ou email paypal"))
                if not is_confirmed:
                    messages.error(request,  _(u"Vérifiez que vous avez bien répondu à l'email d'activation de Paypal"))    
                return redirect_to(request, profile_edit_url)
        else: 
            paypal_redirect = patron.create_account(return_url=return_url)
            if paypal_redirect:
                return redirect_to(request, paypal_redirect)
        patron.paypal_email = None
        patron.save()
        messages.error(request, _(u"Nous n'avons pas pu créer votre compte paypal"))
    return direct_to_template(request, 'accounts/patron_paypal.html', extra_context={'form': form, 'next': redirect_path})


@login_required
def dashboard(request):
    return direct_to_template(request, 'accounts/dashboard.html')


@login_required
def owner_booking(request, page=None):
    queryset = request.user.bookings.exclude(state__in=[Booking.STATE.AUTHORIZING, Booking.STATE.CLOSED, Booking.STATE.REJECTED])
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

@login_required
def alert_edit(request, page=None):
    queryset = request.user.alerts.all()
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/alert_edit.html',
        template_object_name='alert')


@mobify
def contact(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        headers = {'Reply-To': form.cleaned_data['sender']}
        if form.cleaned_data.get('cc_myself'):
            headers['Cc'] = form.cleaned_data['sender']
        
        domain = ".".join(Site.objects.get_current().domain.split('.')[1:])
        email = EmailMessage(form.cleaned_data['subject'], form.cleaned_data['message'],
            settings.DEFAULT_FROM_EMAIL, ['contact@%s' % domain], headers=headers)
        try:
            email.send()
            messages.success(request, _(u"Votre message a bien été envoyé"))
        except (BadHeaderError, smtplib.SMTPException, socket.error):
            messages.error(request, _(u"Erreur lors de l'envoi du message"))
    return direct_to_template(request, 'accounts/contact.html', extra_context={'form': ContactForm()})

    
    
    
    
    
