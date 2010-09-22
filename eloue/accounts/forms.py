# -*- coding: utf-8 -*-
import django.forms as forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _

from eloue.accounts.models import Patron

class EmailAuthenticationForm(AuthenticationForm):
    """Displays the login form and handles the login action."""
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={ 
        'autocapitalize':'off', 'autocorrect':'off'
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput, required=True)
    
    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            email = email.lower()
            self.user_cache = authenticate(username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_(u"Veuillez saisir une adresse email et un mot de passe valide."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_(u"Ce compte est inactif parce qu'il n'a pas été activé."))
        
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
        
        return self.cleaned_data
    
    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None
    
    def get_user(self):
        return self.user_cache
    

class EmailPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("E-mail"), max_length=75, widget=forms.TextInput(attrs={ 
        'autocapitalize':'off', 'autocorrect':'off'
    }))
    
    def save(self, domain_override=None, use_https=False, token_generator=default_token_generator, **kwargs):
        """Generates a one-use only link for resetting password and sends to the user"""
        from django.core.mail import EmailMultiAlternatives 
        for user in self.users_cache:
            if not domain_override:
                current_site = Site.objects.get_current()
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = render_to_string('accounts/password_reset_email_subject.txt', { 'site':Site.objects.get_current() })
            text_content = render_to_string('accounts/password_reset_email.txt', context)
            html_content = render_to_string('accounts/password_reset_email.html', context)
            message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            message.attach_alternative(html_content, "text/html")
            message.send()
    

class PatronChangeForm(forms.ModelForm):
    class Meta:
        model = Patron
    
