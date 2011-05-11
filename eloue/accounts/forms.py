# -*- coding: utf-8 -*-
import types
import re

import django.forms as forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.forms.fields import EMPTY_VALUES
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _

from eloue.accounts import EMAIL_BLACKLIST
from eloue.accounts.fields import PhoneNumberField
from eloue.accounts.models import Patron, PhoneNumber, COUNTRY_CHOICES, PatronAccepted
from eloue.accounts.widgets import ParagraphRadioFieldRenderer
from eloue.utils import form_errors_append
from eloue.rent.payments.paypal_payment import verify_paypal_account


STATE_CHOICES = (
    (0, _(u"Je n'ai pas encore de compte e-loue")),
    (1, _(u"J'ai déjà un compte e-loue et mon mot de passe est :")),
)

PAYPAL_ACCOUNT_CHOICES = (
    (0, _(u"Je n'ai pas encore de compte PayPal")),
    (1, _(u"J'ai déjà un compte PayPal et mon email est :")),
)


class EmailAuthenticationForm(forms.Form):
    """Displays the login form and handles the login action."""
    exists = forms.TypedChoiceField(required=True, coerce=int, choices=STATE_CHOICES, widget=forms.RadioSelect(renderer=ParagraphRadioFieldRenderer), initial=1)
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm', 'tabindex': '1'
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(attrs={'class': 'inm', 'tabindex': '2'}), required=False)
    
    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        exists = self.cleaned_data.get('exists')
        for rule in EMAIL_BLACKLIST:
            if re.search(rule, email):
                raise forms.ValidationError(_(u"Pour garantir un service de qualité et la sécurité des utilisateurs de e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
        
        if not settings.AUTHENTICATION_BACKENDS[0] == 'eloue.accounts.auth.PrivatePatronModelBackend':
            if not exists and Patron.objects.filter(email=email).exists():
                raise forms.ValidationError(_(u"Un compte existe déjà pour cet email"))
                
        if settings.AUTHENTICATION_BACKENDS[0] == 'eloue.accounts.auth.PrivatePatronModelBackend':
            if not exists and not PatronAccepted.objects.filter(email=email, sites=Site.objects.get_current()).exists():
                raise forms.ValidationError(_(u"Une addresse email dcns est obligatoire"))
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
    email = forms.EmailField(label=_("Email"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inb'
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
            subject = render_to_string('accounts/password_reset_email_subject.txt', {'patron': user, 'site': Site.objects.get_current()})
            text_content = render_to_string('accounts/password_reset_email.txt', context)
            html_content = render_to_string('accounts/password_reset_email.html', context)
            message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            message.attach_alternative(html_content, "text/html")
            message.send()
    

class PatronEditForm(forms.ModelForm):
    
    username = forms.RegexField(label=_(u"Pseudo"), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
        widget=forms.TextInput(attrs={'class': 'inm'}))
    first_name = forms.CharField(label=_(u"Prénom"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    last_name = forms.CharField(label=_(u"Nom"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    email = forms.EmailField(label=_(u"Email"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    paypal_email = forms.EmailField(label=_(u"PayPal Email"), required=False, max_length=75, widget=forms.TextInput(attrs={
            'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    is_professional = forms.BooleanField(label=_(u"Êtes-vous un professionnel ?"), required=False, initial=False)
    company_name = forms.CharField(label=_(u"Nom de la société"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}))
    is_subscribed = forms.BooleanField(required=False, initial=False)
    
    def __init__(self, *args, **kwargs):
        super(PatronEditForm, self).__init__(*args, **kwargs)
        self.fields['civility'].widget.attrs['class'] = "selm"
        
        #if kwargs.has_key('sender'):
        #    if kwargs['sender']:
        #        self.sender = kwargs['sender']
        #self.receiver = kwargs['receiver']
    
    def __call__(self):
        paypal_email = self.instance.paypal_email
        if paypal_email:
            is_verified = verify_paypal_account(
                    email=paypal_email,
                    first_name=self.instance.first_name,
                    last_name=self.instance.last_name
                    )
            if not is_verified:
                form_errors_append(self, 'paypal_email', 'Votre paypal email ne correspond pas à votre nom et prénom')
                form_errors_append(self, 'first_name', 'Votre prénom ne correspond pas à votre nom et paypal email')
                form_errors_append(self, 'last_name', 'Votre nom ne correspond pas à votre prénom et paypal email')
                
    def clean_company_name(self):
        is_professional = self.cleaned_data.get('is_professional')
        company_name = self.cleaned_data.get('company_name', None)
        if is_professional and not company_name:
            raise forms.ValidationError(_(u"Vous devez entrer le nom de votre société"))
        return company_name
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if email in EMPTY_VALUES:
            raise forms.ValidationError(_(u"This field is required."))
        for rule in EMAIL_BLACKLIST:
            if re.search(rule, email):
                raise forms.ValidationError(_(u"Pour garantir un service de qualité et la sécurité des utilisateurs de Croisé dans le métro, vous ne pouvez pas vous enregistrer avec une adresse email jetable. Ne craignez rien, vous ne recevrez aucun courrier indésirable."))
        try:
            Patron.objects.exclude(pk=self.instance.pk).get(email=email)
            raise forms.ValidationError(_(u"Un compte avec cet email existe déjà"))
        except Patron.DoesNotExist:
            return email
   
    def clean(self):
        paypal_email = self.cleaned_data.get('paypal_email', None)
        first_name = self.cleaned_data.get('first_name', None)
        last_name = self.cleaned_data.get('last_name', None)
        if paypal_email:
            is_verified = verify_paypal_account(
                        email=paypal_email,
                        first_name=first_name,
                        last_name=last_name
                        )
            if not is_verified:
                print ">>>>>>in form clean non verified>>>>>>>>"
                form_errors_append(self, 'paypal_email', 'Votre paypal email ne correspond pas à votre nom et prénom')
                form_errors_append(self, 'first_name', 'Votre prénom ne correspond pas à votre nom et paypal email')
                form_errors_append(self, 'last_name', 'Votre nom ne correspond pas à votre prénom et paypal email')
            else:
                self.instance.paypal_email = paypal_email
                self.instance.first_name = first_name
                self.instance.last_name = last_name
                self.instance.save()
            print ">>>>>>>>form errors>>>>>>>>>>>", self.errors
        return self.cleaned_data
        
    class Meta:
        model = Patron
        fields = ('civility', 'username', 'first_name', 'last_name',
            'email', 'paypal_email', 'is_professional', 'company_name', 'is_subscribed')
            
            
class PatronPasswordChangeForm(PasswordChangeForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'inm'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'inm'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'inm'}))
    
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
    PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']
    

class PatronChangeForm(forms.ModelForm):
    class Meta:
        model = Patron
    

class PatronPaypalForm(forms.ModelForm):
    paypal_email = forms.EmailField(required=False, label=_("E-mail"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    paypal_exists = forms.TypedChoiceField(required=True, coerce=int, choices=PAYPAL_ACCOUNT_CHOICES, widget=forms.RadioSelect(renderer=ParagraphRadioFieldRenderer), initial=1)
    
    def clean(self):
        paypal_email = self.cleaned_data.get('paypal_email', None)
        paypal_exists = self.cleaned_data['paypal_exists']
        self.paypal_exists = False
        if paypal_exists:
            self.paypal_exists = True
        if not paypal_email:
            if paypal_exists:
                raise forms.ValidationError(_(u"Vous devez entrer votre email Paypal"))
            else:
                self.cleaned_data['paypal_email'] = self.instance.email
        return self.cleaned_data
    
    class Meta:
        model = Patron
        fields = ('paypal_email',)
    

class PhoneNumberForm(forms.ModelForm):
    number = PhoneNumberField()
       
    class Meta:
        model = PhoneNumber
        exclude = ('patron')
    

def make_missing_data_form(instance, required_fields=[]):
    fields = SortedDict({
        'username': forms.RegexField(label=_(u"Pseudo"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
            widget=forms.TextInput(attrs={'class': 'inm'})
        ),
        'password1': forms.CharField(label=_(u"Mot de passe"), max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'inm'})),
        'password2': forms.CharField(label=_(u"A nouveau"), max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'inm'})),
        'is_professional': forms.BooleanField(label=_(u"Êtes-vous un professionnel ?"), required=False, initial=False),
        'company_name': forms.CharField(label=_(u"Nom de la société"), required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'inm'})),
        'first_name': forms.CharField(label=_(u"Prénom"), max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'last_name': forms.CharField(label=_(u"Nom"), max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'addresses__address1': forms.CharField(max_length=255, widget=forms.Textarea(attrs={'class': 'inm street', 'placeholder': _(u'Rue')})),
        'addresses__zipcode': forms.CharField(required=True, max_length=9, widget=forms.TextInput(attrs={
            'class': 'inm zipcode', 'placeholder': _(u'Code postal')
        })),
        'addresses__city': forms.CharField(required=True, max_length=255, widget=forms.TextInput(attrs={'class': 'inm town', 'placeholder': _(u'Ville')})),
        'addresses__country': forms.ChoiceField(choices=COUNTRY_CHOICES, required=True, widget=forms.Select(attrs={'class': 'selm'})),
        'phones__phone': PhoneNumberField(label=_(u"Téléphone"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    })
    
    # Do we have an address ?
    if instance and instance.addresses.exists():
        fields['addresses'] = forms.ModelChoiceField(label=_(u"Addresse"), required=False,
            queryset=instance.addresses.all(), widget=forms.Select(attrs={'class': 'selm'}))
        for f in fields.keys():
            if "addresses" in f:
                fields[f].required = False
    
    # Do we have a phone number ?
    if instance and instance.phones.exists():
        fields['phones'] = forms.ModelChoiceField(label=_(u"Téléphone"), required=False, queryset=instance.phones.all(), widget=forms.Select(attrs={'class': 'selm'}))
        fields['phones__phone'].required = False
    
    # Do we have a password ?
    if instance and instance.password:
        del fields['password1']
        del fields['password2']
    
    # Are we in presence of a pro ?
    if instance and instance.is_professional != None:
        del fields['is_professional']
        del fields['company_name']
    
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
        if Patron.objects.filter(slug=slugify(self.cleaned_data['username'])).exists():
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
    
    def clean_company_name(self):
        is_professional = self.cleaned_data.get('is_professional')
        company_name = self.cleaned_data.get('company_name', None)
        if is_professional and not company_name:
            raise forms.ValidationError(_(u"Vous devez entrer le nom de votre société"))
        return company_name
    
    def clean_phones(self):
        phones = self.cleaned_data['phones']
        phone = self.cleaned_data['phones__phone']
        
        if not phones and not phone:
            raise forms.ValidationError(_(u"Vous devez spécifiez un numéro de téléphone"))
        return phones
    
    form_class = type('MissingInformationForm', (forms.BaseForm,), {'instance': instance, 'base_fields': fields})
    form_class.save = types.MethodType(save, None, form_class)
    form_class.clean_password2 = types.MethodType(clean_password2, None, form_class)
    form_class.clean_username = types.MethodType(clean_username, None, form_class)
    form_class.clean_phones = types.MethodType(clean_phones, None, form_class)
    form_class.clean_addresses = types.MethodType(clean_addresses, None, form_class)
    form_class.clean_company_name = types.MethodType(clean_company_name, None, form_class)
    return fields != {}, form_class
    

class ContactForm(forms.Form):
    subject = forms.CharField(label=_(u"Sujet"), max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    message = forms.CharField(label=_(u"Message"), required=True, widget=forms.Textarea(attrs={'class': 'inm'}))
    sender = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'
    }))
    cc_myself = forms.BooleanField(label=_(u"Je souhaite recevoir une copie de ce message."), required=False)


class PatronSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super(PatronSetPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = 'inm'
        self.fields['new_password2'].widget.attrs['class'] = 'inm'
    
