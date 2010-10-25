# -*- coding: utf-8 -*-
from logbook import Logger

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import Site, RequestSite
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_detail

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron

log = Logger('eloue.accounts')

@never_cache
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    is_actived = Patron.objects.activate(activation_key)
    return direct_to_template(request, 'accounts/activate.html', extra_context={ 'is_actived':is_actived, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS })

def patron_detail(request, slug, patron_id=None):
    if patron_id: # This is here to be compatible with the old app
        return redirect_to(request, reverse('patron_detail', args=[slug]))
    else:
        return object_detail(request, queryset=Patron.objects.all(), slug=slug, template_object_name='patron')

@never_cache
def authenticate(request):
    """Displays the login form and handles the login action"""
    redirect_path = request.REQUEST.get('next', '')
    form = EmailAuthenticationForm(request.POST or None)
    if form.is_valid():
        # Light security check -- make sure redirect_to isn't garbage.
        if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
            redirect_path = settings.LOGIN_REDIRECT_URL
        new_patron = form.get_user()
        if not new_patron:
            new_patron = Patron.objects.create_inactive(form.cleaned_data['email'], form.cleaned_data['password'])
        if not hasattr(new_patron, 'backend'):
            from django.contrib.auth import load_backend
            backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
            new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, new_patron)
        if request.user.is_active:
            messages.success(request, _(u"Bienvenue !"))
        else: # TODO : Maybe warning or info is better suited here, we need to see with design 
            messages.success(request, _(u"Bienvenue ! Nous vous avons envoyé un lien de validation par email. Il est impératif que vous cliquiez dessus pour terminer votre enregistrement."))
        return redirect_to(request, redirect_path)
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return direct_to_template(request, template='accounts/login.html', extra_context={ 'form':form, 'next':redirect_path, 'site_name':current_site.name })

