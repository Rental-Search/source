# -*- coding: utf-8 -*-
import re

import django.forms as forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _

from eloue.accounts import EMAIL_BLACKLIST
from eloue.accounts.fields import PhoneNumberField
from eloue.accounts.models import Patron, PhoneNumber, Address

PATRON_FIELDS = ['first_name', 'last_name', 'username']
ADDRESS_FIELDS = ['address1', 'address2', 'zipcode', 'city', 'country']


class EmailAuthenticationForm(forms.Form):
    """Displays the login form and handles the login action."""
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={ 
        'autocapitalize':'off', 'autocorrect':'off'
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput, required=True)
    
    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        for rule in EMAIL_BLACKLIST:
            if re.search(rule, email):
                raise forms.ValidationError(_(u"Pour garantir un service de qualité et la sécurité des utilisateurs de e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
        return email
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            email = email.lower()
            if Patron.objects.filter(email=email).exists():
                self.user_cache = authenticate(username=email, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError(_(u"Veuillez saisir une adresse email et un mot de passe valide."))
                elif not self.user_cache.is_active:
                    raise forms.ValidationError(_(u"Ce compte est inactif parce qu'il n'a pas été activé."))
        
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
    

class PhoneNumberForm(forms.ModelForm):
    number = PhoneNumberField()
       
    class Meta:
        model = PhoneNumber
        exclude = ('patron')
    

def fields_for_instance(instance, fields=None, exclude=None, widgets=None):
    field_list = []
    opts = instance._meta
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if hasattr(instance, f.name) and getattr(instance, f.name):
            continue
        if widgets and f.name in widgets:
            kwargs = {'widget': widgets[f.name]}
        else:
            kwargs = {}
        formfield = f.formfield(**kwargs)
        if formfield:
            field_list.append((f.name, formfield))
    return SortedDict(field_list)

def make_missing_data_form(instance):
    fields = {}
    if instance:
        fields.update(fields_for_instance(instance, fields=PATRON_FIELDS))
        if instance.addresses.exists():
            fields.update({ 'address':forms.ModelChoiceField(queryset=instance.addresses.all()) })
        fields.update(fields_for_instance(Address, exclude=['patron']))
    else:
        fields.update(fields_for_instance(Patron, fields=PATRON_FIELDS))
        fields.update(fields_for_instance(Address, exclude=['patron']))
    form_class = type('MissingInformationForm', (forms.BaseForm,), { 'base_fields': fields })
    return fields != {}, form_class
