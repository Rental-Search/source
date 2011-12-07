# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron, Avatar
from eloue.wizard import MultiPartFormWizard, NewGenericFormWizard

class AuthenticationWizard(NewGenericFormWizard):

    def __init__(self, *args, **kwargs):
        super(AuthenticationWizard, self).__init__(*args, **kwargs)
        self.required_fields = ['username', 'password1', 'password2', 'is_professional', 'company_name', 'avatar']
    
    def done(self, request, form_list):
        super(AuthenticationWizard, self).done(request, form_list)
        if request.user.is_active:
            GoalRecord.record('authentication', WebUser(request))
            messages.success(request, _(u"Bienvenue !"))
        else:
            GoalRecord.record('registration', WebUser(request))
            messages.info(request, _(u"Bienvenue ! Nous vous avons envoyé un lien de validation par email. Cette validation est impérative pour terminer votre enregistrement."))
        return redirect_to(request, self.redirect_path, permanent=False)
    
    def parse_params(self, request, *args, **kwargs):
        redirect_path = request.REQUEST.get('next', '')
        if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
            self.redirect_path = settings.LOGIN_REDIRECT_URL
        else:
            self.redirect_path = redirect_path
        
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        else:
            return 'accounts/auth_missing.html'
    
