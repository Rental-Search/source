# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.utils.translation import ugettext as _
from django.views.generic.simple import redirect_to

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron
from eloue.wizard import CustomFormWizard

class AuthenticationWizard(CustomFormWizard):
    def done(self, request, form_list):
        missing_form = form_list[-1]
        
        auth_form = form_list[-2]
        new_patron = auth_form.get_user()
        if not new_patron:
            new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'], 
                auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
        if not hasattr(new_patron, 'backend'):
            from django.contrib.auth import load_backend
            backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
            new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, new_patron)
        
        missing_form.instance = new_patron
        new_patron, new_address, new_phone = missing_form.save()
        
        if request.user.is_active:
            messages.success(request, _(u"Bienvenue !"))
        else: # TODO : Maybe warning or info is better suited here, we need to see with design
            messages.success(request, _(u"Bienvenue ! Nous vous avons envoyé un lien de validation par email. Cette validation est impérative pour terminer votre enregistrement."))
        return redirect_to(request, self.redirect_path)
    
    def parse_params(self, request, *args, **kwargs):
        redirect_path = request.REQUEST.get('next', '')
        if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
            self.redirect_path = settings.LOGIN_REDIRECT_URL
        else:
            self.redirect_path = redirect_path
    
    def __call__(self, request, *args, **kwargs):
        if EmailAuthenticationForm not in self.form_list:
            self.form_list.append(EmailAuthenticationForm)
        if EmailAuthenticationForm in self.form_list:
            if not any(map(lambda el: getattr(el, '__name__', None) == 'MissingInformationForm', self.form_list)):
                form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                form.is_valid() # Here to fill form user_cache
                self.form_list.append(make_missing_data_form(form.get_user()))
        return super(AuthenticationWizard, self).__call__(request, *args, **kwargs)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        else:
            return 'accounts/auth_missing.html'
    
