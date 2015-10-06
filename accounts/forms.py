# -*- coding: utf-8 -*-
from __future__ import absolute_import
import types
import uuid
import re

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import is_password_usable
from django.contrib.sites.models import Site, get_current_site
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext as _

from form_utils.forms import BetterForm

from payments.paybox_payment import PayboxManager, PayboxException

from .fields import PhoneNumberField, ExpirationField, DateSelectField, CreditCardField
from .models import Patron, CreditCard
from .choices import COUNTRY_CHOICES
from .widgets import CommentedCheckboxInput

mask_card_number_re = re.compile(r'(.)(.*)(...)')


def mask_card_number(card_number):
    return mask_card_number_re.sub(
        lambda matchobject: (
            matchobject.group(1)+'X'*len(matchobject.group(2))+matchobject.group(3)
        ), 
        card_number
    )


class CreditCardForm(forms.ModelForm):
    cvv = forms.CharField(max_length=4, label=_(u'Cryptogramme de sécurité'), help_text=_(u'Les 3 derniers chiffres au dos de la carte.'))
    expires = ExpirationField(label=_(u'Date d\'expiration'))
    holder_name = forms.CharField(label=_(u'Titulaire de la carte'))


    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)
        # see note: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#using-a-subset-of-fields-on-the-form
        # we excluded, then added, to avoid save automatically the card_number. Required by rent.forms.BookingCreditCardForm
        self.fields['card_number'] = CreditCardField(
            label=_(u'Numéro de carte de crédit'), widget=forms.TextInput(
                attrs={'placeholder': self.instance.masked_number or ''}
            )
        )

    class Meta:
        # see note: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#using-a-subset-of-fields-on-the-form
        # we excluded, then added, to avoid save automatically the card_number
        model = CreditCard
        exclude = (
            'card_number', 'masked_number', 'keep', 'subscriber_reference'
        )

    def clean(self):
        try:
            pm = PayboxManager()
            self.cleaned_data['masked_number'] = mask_card_number(self.cleaned_data.get('card_number', ''))
            pm.authorize(self.cleaned_data['card_number'], 
                self.cleaned_data['expires'], self.cleaned_data['cvv'], 1, 'verification'
            )
        except PayboxException as err:
            raise forms.ValidationError(_(u'La validation de votre carte a échoué: ({0}) {1}').format(*err.args))
        return self.cleaned_data

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        pm = PayboxManager()
        if self.instance.pk:
            self.cleaned_data['card_number'] = pm.modify(
                self.instance.subscriber_reference,
                self.cleaned_data['card_number'],
                self.cleaned_data['expires'], self.cleaned_data['cvv'])
        else:
            self.cleaned_data['card_number'] = pm.subscribe(
                self.instance.subscriber_reference,
                self.cleaned_data['card_number'],
                self.cleaned_data['expires'], self.cleaned_data['cvv']
            )
        instance = super(CreditCardForm, self).save(*args, commit=False, **kwargs)
        instance.card_number = self.cleaned_data['card_number']
        instance.masked_number = self.cleaned_data['masked_number']
        if commit:
            instance.save()
        return instance


class EmailPasswordResetForm(forms.Form):
    error_messages = {
        'unknown': _("That email address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this email "
                      "address cannot reset the password."),
    }

    email = forms.EmailField(label=_("Email"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inb'
    }))

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data['email']
        self.users_cache = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any(not is_password_usable(user.password)
               for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(self, domain_override=None,
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             request=None, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import EmailMultiAlternatives
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request) if request else Site.objects.get_current()
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'patron': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = render_to_string(email_template_name + '_subject.txt', context)
            text_content = render_to_string(email_template_name + '.txt', context)
            html_content = render_to_string(email_template_name + '.html', context)
            message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            message.attach_alternative(html_content, "text/html")
            message.send()


class PatronSetPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput(attrs={'class': 'inm'}))
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput(attrs={'class': 'inm'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PatronSetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.user is None:
            raise forms.ValidationError(_("User record is empty."))
        return self.cleaned_data

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


# Django Admin : see admin.py


class PatronChangeForm(forms.ModelForm):
    class Meta:
        model = Patron


class PatronCreationForm(UserCreationForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."), required=False)
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=True)
    first_name = forms.CharField(label=_(u"Prénom"), required=True)
    last_name = forms.CharField(label=_(u"Nom"), required=True)

    def __init__(self, *args, **kwargs):
        super(PatronCreationForm, self).__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_company_name(self):
        is_professional = self.cleaned_data.get('is_professional')
        company_name = self.cleaned_data.get('company_name', None)
        if is_professional and not company_name:
            raise forms.ValidationError(_(u"Vous devez entrer le nom de l'entreprise"))
        return company_name

    def clean_slug(self):
        slug = self.cleaned_data.get("username", "")
        return slugify(slug)

    def clean(self):
        if self.cleaned_data.get("is_professional"):
            self.cleaned_data['password1'] = None
            self.cleaned_data['password2'] = None
        else:
            msg = _(u"Ce champ est obligatoire.")
            if not self.cleaned_data.get("password1"):
                self._errors["password1"] = self.error_class([msg])
                if 'password1' in self.cleaned_data:
                    del self.cleaned_data["password1"]
            if not self.cleaned_data.get("password2"):
                self._errors["password2"] = self.error_class([msg])
                if 'password2' in self.cleaned_data:
                    del self.cleaned_data["password2"]
        return self.cleaned_data

    class Meta:
        model = Patron


def mask_card_number(card_number):
    return re.sub(
        '(.)(.*)(...)', 
        lambda matchobject: (
            matchobject.group(1)+'X'*len(matchobject.group(2))+matchobject.group(3)
        ), 
        card_number
    )


class CreditCardForm(forms.ModelForm):
    cvv = forms.CharField(max_length=4, label=_(u'Cryptogramme de sécurité'), help_text=_(u'Les 3 derniers chiffres au dos de la carte.'))
    expires = ExpirationField(label=_(u'Date d\'expiration'))
    holder_name = forms.CharField(label=_(u'Titulaire de la carte'))

    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)
        # see note: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#using-a-subset-of-fields-on-the-form
        # we excluded, then added, to avoid save automatically the card_number. Required by rent.forms.BookingCreditCardForm
        self.fields['card_number'] = CreditCardField(
            label=_(u'Numéro de carte de crédit'), widget=forms.TextInput(
                attrs={'placeholder': self.instance.masked_number or ''}
            )
        )

    class Meta:
        # see note: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#using-a-subset-of-fields-on-the-form
        # we excluded, then added, to avoid save automatically the card_number
        model = CreditCard
        exclude = (
            'card_number', 'masked_number', 'keep', 'subscriber_reference'
        )

    def clean(self):
        cleaned_data = super(CreditCardForm, self).clean()
        try:
            card_number = cleaned_data['card_number']
            expires = cleaned_data['expires']
            cvv = cleaned_data['cvv']
        except KeyError:
            pass
        else:
            # attempt to verify the credit card information through the payment API
            try:
                pm = PayboxManager()
                self.cleaned_data['masked_number'] = mask_card_number(card_number)
                pm.authorize(card_number, expires, cvv, 1, 'verification')
            except PayboxException as err:
                raise forms.ValidationError(_(u'La validation de votre carte a échoué: ({0}) {1}').format(*err.args))
        return self.cleaned_data

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        pm = PayboxManager()
        if self.instance.pk:
            self.cleaned_data['card_number'] = pm.modify(
                self.instance.subscriber_reference,
                self.cleaned_data['card_number'],
                self.cleaned_data['expires'], self.cleaned_data['cvv'])
        else:
            self.cleaned_data['card_number'] = pm.subscribe(
                self.instance.subscriber_reference,
                self.cleaned_data['card_number'],
                self.cleaned_data['expires'], self.cleaned_data['cvv']
            )
        instance = super(CreditCardForm, self).save(*args, commit=False, **kwargs)
        instance.card_number = self.cleaned_data['card_number']
        instance.masked_number = self.cleaned_data['masked_number']
        if commit:
            instance.save()
        return instance


def make_missing_data_form(instance, required_fields=[]):
    fields = SortedDict({
        'is_professional': forms.BooleanField(label=_(u"Professionnel"), required=False, initial=False, widget=CommentedCheckboxInput(info_text='Je suis professionnel')),
        'company_name': forms.CharField(label=_(u"Nom de la société"), required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'inm'})),
        'username': forms.RegexField(label=_(u"Pseudo"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
            widget=forms.TextInput(attrs={'class': 'inm'})
        ),
        'password1': forms.CharField(label=_(u"Mot de passe"), max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'inm'})),
        'password2': forms.CharField(label=_(u"Mot de passe à nouveau"), max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'inm'})),
        'first_name': forms.CharField(label=_(u"Prénom"), max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'last_name': forms.CharField(label=_(u"Nom"), max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'addresses__address1': forms.CharField(label=_(u"Rue"), max_length=255, widget=forms.Textarea(attrs={'class': 'inm street'})),
        'addresses__zipcode': forms.CharField(label=_(u"Code postal"), required=True, max_length=9, widget=forms.TextInput(attrs={
            'class': 'inm zipcode'
        })),
        'addresses__city': forms.CharField(label=_(u"Ville"), required=True, max_length=255, widget=forms.TextInput(attrs={'class': 'inm town'})),
        'addresses__country': forms.ChoiceField(label=_(u"Pays"), choices=COUNTRY_CHOICES, required=True, widget=forms.Select(attrs={'class': 'selm'})),
        'avatar': forms.ImageField(required=False, label=_(u"Photo de profil")),
        'phones__phone': PhoneNumberField(label=_(u"Téléphone"), required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'drivers_license_number': forms.CharField(label=_(u'Numéro de permis'), max_length=32),
        'drivers_license_date': DateSelectField(label=_(u'Date de délivraisance')),
        'date_of_birth': DateSelectField(label=_(u'Date de naissance')),
        'place_of_birth': forms.CharField(label=_(u'Lieu de naissance'), max_length=255),
        'cvv': forms.CharField(max_length=4, label=_(u'Cryptogramme de sécurité'), help_text=_(u'Les 3 derniers chiffres au dos de la carte.')),
        'expires': ExpirationField(label=_(u'Date d\'expiration')),
        'holder_name': forms.CharField(label=_(u'Titulaire de la carte')),
        'card_number': CreditCardField(label=_(u'Numéro de carte de crédit')),
        'godfather_email': forms.EmailField(label=_(u'Email de votre parrain'), required=False, help_text=_(u'Commissions offertes pendant 3 mois si vous êtes parrainé par membre e-loue. Offre valable entre le 18 avril et le 30 avril 2013.')),
    })


    # Are we in presence of a pro ?
    if fields.has_key('is_professional'):
        if instance and getattr(instance, 'is_professional', None)!=None:
            del fields['is_professional']
            del fields['company_name']

    # Do we have an address ?
    if instance and instance.addresses.exists():
        fields['addresses'] = forms.ModelChoiceField(label=_(u"Adresse"), required=False,
            queryset=instance.addresses.all(), initial=instance.default_address if instance.default_address else instance.addresses.all()[0], widget=forms.Select(attrs={'class': 'selm'}), help_text=_(u"Selectionnez une adresse enregistrée précédemment"))
        for f in fields.keys():
            if "addresses" in f:
                fields[f].required = False
    
    # Do we have a phone number ?
    if instance and instance.phones.exists():
        fields['phones'] = forms.ModelChoiceField(label=_(u"Téléphone"), required=False, 
            queryset=instance.phones.all(), initial=instance.phones.all()[0], widget=forms.Select(attrs={'class': 'selm'}), help_text=_(u"Selectionnez un numéro de téléphone enregistré précédemment"))
        if fields.has_key('phones__phone'):
            fields['phones__phone'].required = False
    
    # Do we have a password ?
    if fields.has_key('password1'):
        if instance and getattr(instance, 'password', None):
            del fields['password1']
            del fields['password2']
    
    if instance and instance.username and "first_name" not in required_fields:
        del fields['avatar']
    
    if instance:
        try:
            if instance.creditcard:
                del fields['cvv']
                del fields['expires']
                del fields['holder_name']
                del fields['card_number']
        except CreditCard.DoesNotExist:
            pass

    for f in fields.keys():
        if required_fields and f not in required_fields:
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
            if "addresses" not in attr and "phones" not in attr: # wtf is this checking?
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
            self.instance.default_address = address
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
        if self.cleaned_data.get('card_number'):
            pm = PayboxManager()
            subscriber_reference = uuid.uuid4().hex
            self.cleaned_data['card_number'] = pm.subscribe(
                subscriber_reference,
                self.cleaned_data['card_number'], 
                self.cleaned_data['expires'], self.cleaned_data['cvv']
            )
            credit_card = CreditCard.objects.create(
                subscriber_reference=subscriber_reference,
                masked_number=self.cleaned_data['masked_number'],
                card_number=self.cleaned_data['card_number'],
                holder_name=self.cleaned_data['holder_name'],
                expires=self.cleaned_data['expires'],
                holder=self.instance, keep=True
            )
        else:
            credit_card = None

        self.instance.save()
        return self.instance, address, phone, credit_card
    
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
    
    def clean(self):
        if self.errors:
            return self.cleaned_data

        if self.cleaned_data.get('card_number'):
            try:
                pm = PayboxManager()
                self.cleaned_data['masked_number'] = mask_card_number(self.cleaned_data['card_number'])
                pm.authorize(self.cleaned_data['card_number'], 
                    self.cleaned_data['expires'], self.cleaned_data['cvv'], 1, 'verification'
                )
            except PayboxException:
                raise forms.ValidationError(_(u'La validation de votre carte a échoué.'))
        
        # testing passwords against each other:
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 != password2:
            msg = _(u"Vos mots de passe ne correspondent pas")
            self._errors['password1'] = [msg]
            self._errors['password2'] = [msg]
            del self.cleaned_data['password1']
            del self.cleaned_data['password2']

        return self.cleaned_data

    class Meta:
        fieldsets = [
            ('member', {
                'fields': ['is_professional', 'company_name', 'username', 'password1', 'password2', 'first_name', 'last_name', 'avatar', 'godfather_email','date_of_birth', 'place_of_birth'], 
                'legend': 'Vous'}),
            ('driver_info', {
                'fields': ['drivers_license_number', 'drivers_license_date'],
                'legend': _(u'Permis de conduire')}),
            ('contacts', {
                'fields': ['addresses', 'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country', 'phones', 'phones__phone'], 
                'legend': 'Vos coordonnées'}),
            ('payment', {
                'fields': ['cvv', 'expires', 'holder_name', 'card_number', ],
                'legend': 'Vos coordonnées bancaires'
                }),
        ]

    class_dict = fields.copy()
    class_dict.update({'instance': instance, 'Meta': Meta})
    form_class = type('MissingInformationForm', (BetterForm,), class_dict)
    form_class.save = types.MethodType(save, None, form_class)
    form_class.clean = types.MethodType(clean, None, form_class)
    form_class.clean_username = types.MethodType(clean_username, None, form_class)
    form_class.clean_phones = types.MethodType(clean_phones, None, form_class)
    form_class.clean_addresses = types.MethodType(clean_addresses, None, form_class)
    form_class.clean_company_name = types.MethodType(clean_company_name, None, form_class)
    return fields != {}, form_class


class ContactFormPro(forms.Form):
    name = forms.CharField(max_length=100, initial="")
    sender = forms.EmailField(max_length=50, initial="")
    phone_number = forms.CharField(max_length= 12, required=False, initial="")
    activity_field = forms.CharField(max_length=100, initial="")


class ContactForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, initial="")
    sender = forms.EmailField(label='Your name', max_length=100, initial="")
    category = forms.CharField(widget=forms.Select)
    cc_myself = forms.BooleanField(required=False)
