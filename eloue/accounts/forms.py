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
from django.utils.datastructures import SortedDict
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _

from eloue.accounts import EMAIL_BLACKLIST
from eloue.accounts.fields import PhoneNumberField
from eloue.accounts.models import Patron, PhoneNumber, COUNTRY_CHOICES
from eloue.accounts.widgets import CustomRadioFieldRenderer

STATE_CHOICES = (
    (0, "Je n'ai pas encore de compte e-loue"),
    (1, "J'ai déjà un compte e-loue et mon mot de passe est :"),
)


class EmailAuthenticationForm(forms.Form):
    """Displays the login form and handles the login action."""
    exists = forms.TypedChoiceField(required=True, coerce=int, choices=STATE_CHOICES, widget=forms.RadioSelect(renderer=CustomRadioFieldRenderer), initial=1)
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={
        'autocapitalize':'off', 'autocorrect':'off', 'class':'inb'
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(attrs={'class':'inb'}), required=False)
    
    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        exists = self.cleaned_data.get('exists')
        for rule in EMAIL_BLACKLIST:
            if re.search(rule, email):
                raise forms.ValidationError(_(u"Pour garantir un service de qualité et la sécurité des utilisateurs de e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
        if not exists and Patron.objects.filter(email=email).exists():
            raise forms.ValidationError(_(u"Un compte existe déjà pour cet email"))
        return email
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        exists = self.cleaned_data.get('exists')
        
        if exists:
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
        'autocapitalize':'off', 'autocorrect':'off', 'class':'inb'
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
                'patron': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = render_to_string('accounts/password_reset_email_subject.txt', { 'patron':user, 'site':Site.objects.get_current() })
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
    

def make_missing_data_form(instance, required_fields=[]):
    fields = SortedDict({
        'username':forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
            widget=forms.TextInput(attrs={'class':'inb'})
        ),
        'password1':forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'inb'})),
        'password2':forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'inb'})),
        'first_name':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb'})),
        'last_name':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb'})),
        'addresses__address1':forms.CharField(widget=forms.Textarea(attrs={'class':'inb street', 'placeholder':'Rue'})),
        'addresses__zipcode':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb zip', 'placeholder':'Code postal'})),
        'addresses__city':forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'inb town', 'placeholder':'Ville'})),
        'addresses__country':forms.ChoiceField(choices=COUNTRY_CHOICES, required=True, widget=forms.Select(attrs={'class':'country'})),
        'phones__phone':PhoneNumberField(required=True, widget=forms.TextInput(attrs={'class':'inb'}))
    })
    
    # Do we have an address ?
    if instance and instance.addresses.exists():
        fields['addresses'] = forms.ModelChoiceField(required=False, queryset=instance.addresses.all(), widget=forms.Select(attrs={'style':'width: 360px;'}))
        for f in fields.keys():
            if "addresses" in f:
                fields[f].required = False
    
    # Do we have a phone number ?
    if instance and instance.phones.exists():
        fields['phones'] = forms.ModelChoiceField(required=False, queryset=instance.phones.all())
        fields['phones__phone'].required = False
    
    # Do we have a password ?
    if instance and instance.password:
        del fields['password1']
        del fields['password2']
        
    for f in fields.keys():
        if f not in required_fields:
            del fields[f]
            continue
        if "__" in f or f in ["addresses", "phones", "password"]:
            continue
        if hasattr(instance, f) and getattr(instance, f):
            del fields[f]
    
    def save(self):
        for attr, value in self.cleaned_data.iteritems():
            if attr == "password1":
                self.instance.set_password(value)
            if "addresses" not in attr and "phones" not in attr:
                setattr(self.instance, attr, value)
        if 'addresses' in self.cleaned_data and self.cleaned_data['addresses']:
            address = self.cleaned_data['addresses']
        elif 'addresses__address1' in self.cleaned_data:
            address = self.instance.addresses.create(
                address1=self.cleaned_data['addresses__address1'],
                zipcode=self.cleaned_data['addresses__zipcode'],
                city=self.cleaned_data['addresses__city'],
                country=self.cleaned_data['addresses__country']
            )
        else:
            address = None
        if 'phones' in self.cleaned_data and self.cleaned_data['phones']:
            phone = self.cleaned_data['phones']
        elif 'phones__phone' in self.cleaned_data:
            phone = self.instance.phones.create(
                number=self.cleaned_data['phones__phone']
            )
        else:
            phone = None
        self.instance.save()
        return self.instance, address, phone
    
    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        
        if password1 != password2:
            raise forms.ValidationError(_(u"Vos mots de passe ne correspondent pas"))
        return self.cleaned_data
    
    def clean_username(self):
        if Patron.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(_(u"Ce nom d'utilisateur est déjà pris."))
        return self.cleaned_data['username']
        
    def clean_addresses(self):
        addresses = self.cleaned_data['addresses']
        address1 = self.cleaned_data['addresses__address1']
        zipcode = self.cleaned_data['addresses__zipcode']
        city = self.cleaned_data['addresses__city']
        country = self.cleaned_data['addresses__country']
        
        if not addresses and not (address1 and zipcode and city and country):
            raise forms.ValidationError(_(u"Vous devez spécifiez une adresse"))
        return self.cleaned_data['addresses']
    
    def clean_phones(self):
        phones = self.cleaned_data['phones']
        phone = self.cleaned_data['phones__phone']
        
        if not phones and not phone:
            raise forms.ValidationError(_(u"Vous devez spécifiez un numéro de téléphone"))
        return phones
    
    form_class = type('MissingInformationForm', (forms.BaseForm,), { 'instance':instance, 'base_fields': fields })
    form_class.save = types.MethodType(save, None, form_class)
    form_class.clean_password2 = types.MethodType(clean_password2, None, form_class)
    form_class.clean_username = types.MethodType(clean_username, None, form_class)
    form_class.clean_phones = types.MethodType(clean_phones, None, form_class)
    form_class.clean_addresses = types.MethodType(clean_addresses, None, form_class)
    return fields != {}, form_class
