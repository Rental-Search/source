# -*- coding: utf-8 -*-
import types
import re

import django.forms as forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _

from eloue.accounts import EMAIL_BLACKLIST
from eloue.accounts.fields import PhoneNumberField
from eloue.accounts.models import Patron, PhoneNumber, COUNTRY_CHOICES

PATRON_FIELDS = ['first_name', 'last_name', 'username']
ADDRESS_FIELDS = ['address1', 'address2', 'zipcode', 'city', 'country']


class EmailAuthenticationForm(forms.Form):
    """Displays the login form and handles the login action."""
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={ 
        'autocapitalize':'off', 'autocorrect':'off', 'class':'inb'
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(attrs={'class':'inb'}), required=True)
    
    def __init__(self, request, *args, **kwargs):
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
    

def make_missing_data_form(instance):
    fields = {
        'username':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb'})),
        'last_name':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb'})),
        'first_name':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb'})),
        'last_name':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb'})),
        'addresses__address1':forms.CharField(widget=forms.Textarea(attrs={'class':'inb street', 'placeholder':'Rue'})),
        'addresses__address2':forms.CharField(required=False),
        'addresses__zipcode':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb zip', 'placeholder':'Code postal'})),
        'addresses__city':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb town', 'placeholder':'Ville'})),
        'addresses__country':forms.ChoiceField(choices=COUNTRY_CHOICES, required=True, widget=forms.Select(attrs={'class':'country'})),
        'phones__phone':PhoneNumberField(required=False, widget=forms.TextInput(attrs={'class':'inb'}))
    }
    if instance and instance.addresses.exists():
        fields['addresses'] = forms.ModelChoiceField(queryset=instance.addresses.all())
    if instance and instance.phones.exists():
        fields['phones'] = forms.ModelChoiceField(queryset=instance.phones.all())
        
    for f in fields.keys():
        if "__" in f:
            continue 
        if hasattr(instance, f) and getattr(instance, f):
            del fields[f]
    
    def save(self):
        for attr, value in self.cleaned_data.iteritems():
            if "__" not in attr:
                setattr(self.instance, attr, value)
        if 'addresses' in self.cleaned_data:
            address = self.cleaned_data['addresses']
        else:
            address = self.instance.addresses.create(
                address1=self.cleaned_data['address1'],
                address2=self.cleaned_data['address2'],
                zipcode=self.cleaned_data['zipcode'],
                city=self.cleaned_data['city'],
                country=self.cleaned_data['country']
            )
        if 'phones' in self.cleaned_data:
            phone = self.cleaned_data['phones']
        elif self.cleaned_data['phone']:
            phone = self.instance.phone.create(
                number=self.cleaned_data['phone']
            )
        else:
            phone = None
        return self.instance, address, phone
    
    def clean_username(self):
        if Patron.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(_(u"Ce nom d'utilisateur est déjà pris."))
    
    form_class = type('MissingInformationForm', (forms.BaseForm,), { 'instance':instance, 'base_fields': fields })
    form_class.save = types.MethodType(save, None, form_class)
    form_class.clean_username = types.MethodType(clean_username, None, form_class)
    return fields != {}, form_class
