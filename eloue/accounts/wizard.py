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
from eloue.wizard import MultiPartFormWizard

def isMissingInformationForm(obj):
    return getattr(obj.__class__, '__name__', None) == 'MissingInformationForm'

class AuthenticationWizard(MultiPartFormWizard):
    required_fields = ['username', 'password1', 'password2', 'is_professional', 'company_name', 'avatar']
    
    def __init__(self, *args, **kwargs):
        super(AuthenticationWizard, self).__init__(*args, **kwargs)
        self.me = None
    
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if isMissingInformationForm(form)), None)
        auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)

        new_patron = auth_form.get_user()
        fb_session = auth_form.fb_session

        if not new_patron:
            if fb_session:
                new_patron = Patron.objects.create_user(
                  missing_form.cleaned_data['username'], 
                  auth_form.cleaned_data['email'], 
                  missing_form.cleaned_data['password1']
                )
                fb_session.user = new_patron
                fb_session.save()
            else:
                new_patron = Patron.objects.create_inactive(
                  missing_form.cleaned_data['username'],
                  auth_form.cleaned_data['email'], 
                  missing_form.cleaned_data['password1']
                )
            
            if hasattr(settings, 'AFFILIATE_TAG'):
                # Assign affiliate tag, no need to save, since missing_form should do it for us
                new_patron.affiliate = settings.AFFILIATE_TAG
            
        if not hasattr(new_patron, 'backend'):
            from django.contrib.auth import load_backend
            backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
            new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, new_patron)
        
        if missing_form:  # Okay, there's nothing missing here
            missing_form.instance = new_patron
            new_patron, new_address, new_phone, avatar = missing_form.save()
            if not avatar and fb_session:
                if 'picture' in self.me:
                    from urllib2 import urlopen
                    from django.core.files.uploadedfile import SimpleUploadedFile

                    fb_image_object = urlopen(self.me['picture']).read()
                    Avatar(patron=new_patron, image=SimpleUploadedFile('picture',fb_image_object)).save()
        
        if request.user.is_active:
            GoalRecord.record('authentication', WebUser(request))
            messages.success(request, _(u"Bienvenue !"))
        else:
            GoalRecord.record('registration', WebUser(request))
            messages.info(request, _(u"Bienvenue ! Nous vous avons envoyé un lien de validation par email. Cette validation est impérative pour terminer votre enregistrement."))
        return redirect_to(request, self.redirect_path, permanent=False)

    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if next_form.__name__ == 'MissingInformationForm':            
            return next_form(
              data=data, 
              files=files, 
              prefix=self.prefix_for_step(step), 
              initial={'username': self.me.get('username', '')}
            )
        return super(AuthenticationWizard, self).get_form(step, data=data, files=files)
    
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
            if not next((form for form in self.form_list if getattr(form, '__name__', None) == 'MissingInformationForm'), None):
                form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                form.is_valid()
                missing_fields, missing_form = make_missing_data_form(form.get_user(), self.required_fields)
                if missing_fields:
                    self.form_list.append(missing_form)
        return super(AuthenticationWizard, self).__call__(request, *args, **kwargs)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        else:
            return 'accounts/auth_missing.html'
    
