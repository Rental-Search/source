# -*- coding: utf-8 -*-
import types
import re
import datetime

import django.forms as forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.forms.fields import EMPTY_VALUES
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _
from django.dispatch import dispatcher
from django.utils.safestring import mark_safe

import facebook

from eloue.accounts import EMAIL_BLACKLIST
from eloue.accounts.fields import PhoneNumberField
from eloue.accounts.models import Patron, Avatar, PhoneNumber, COUNTRY_CHOICES, PatronAccepted, FacebookSession, Address
from eloue.accounts.widgets import ParagraphRadioFieldRenderer
from eloue.utils import form_errors_append
from eloue.payments import paypal_payment


STATE_CHOICES = (
    (0, _(u"Je n'ai pas encore de compte")),
    (1, _(u"J'ai déjà un compte et mon mot de passe est :")),
)

PAYPAL_ACCOUNT_CHOICES = (
    (0, _(u"Je n'ai pas encore de compte PayPal")),
    (1, _(u"J'ai déjà un compte PayPal et mon email est :")),
)

class FacebookForm(forms.Form):
    
    facebook_access_token = forms.CharField(
        required=False, widget=forms.HiddenInput())
    facebook_expires = forms.IntegerField(
        required=False, widget=forms.HiddenInput())
    facebook_uid = forms.CharField(
        required=False, widget=forms.HiddenInput())
    
    def clean(self):
        access_token = self.cleaned_data.get('facebook_access_token', None)
        uid = self.cleaned_data.get('facebook_uid', None)
        expires = self.cleaned_data.get('facebook_expires', None)

        try:
            me = facebook.GraphAPI(access_token).get_object(
                'me', 
                fields=('picture,email,first_name,'
                    'last_name,gender,username,location')
            )
        except facebook.GraphAPIError as e:
            raise forms.ValidationError(e)
        
        if 'id' not in me:
            raise forms.ValidationError(_(
                "Les serveurs de Facebook sont inaccessibles."
                " Veuillez reessayer dans quelques secondes."
            ))
        
        if uid != me['id']:
            raise forms.ValidationError(_(u'Wrong facebook uid.'))
        
        try:
            fb, created = FacebookSession.objects.get_or_create(
                uid=me['id'], 
                defaults={
                    'access_token': access_token, 
                    'expires': (datetime.datetime.now() + 
                        datetime.timedelta(seconds=expires)),
                    'user': self.user
                }
            )
        except FacebookSession.MultipleObjectsReturned:
            raise forms.ValidationError('4')
        
        if not created:
            if fb.user:
                raise forms.ValidationError(
                    _(u'Un compte e-loue est déjà associé à votre Facebook')
                )
            else:
                fb.user = self.user
                fb.save()
        
        return self.cleaned_data

class EmailAuthenticationForm(forms.Form):
    """Displays the login form and handles the login action."""
    exists = forms.TypedChoiceField(required=True, coerce=int, choices=STATE_CHOICES, widget=forms.RadioSelect(renderer=ParagraphRadioFieldRenderer), initial=1)
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=False, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm', 'tabindex': '1'
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(attrs={'class': 'inm', 'tabindex': '2'}), required=False)
    
    # for facebook connect
    facebook_access_token = forms.CharField(required=False, widget=forms.HiddenInput())
    facebook_expires = forms.IntegerField(required=False, widget=forms.HiddenInput())
    facebook_uid = forms.CharField(required=False, widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        self.user_cache = None
        self.fb_session = None
        self.me = None
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

        facebook_access_token = self.cleaned_data.get('facebook_access_token')
        facebook_expires = self.cleaned_data.get('facebook_expires')
        facebook_uid = self.cleaned_data.get('facebook_uid')

        if any([facebook_access_token, facebook_expires, facebook_uid]):
            try:
                self.me = facebook.GraphAPI(facebook_access_token).get_object('me', fields='picture,email,first_name,last_name,gender,username,location')
            except facebook.GraphAPIError as e:
                raise forms.ValidationError(str(e))
            
            if self.me.get('id', None) != facebook_uid:
                raise forms.ValidationError(_(u'Wrong facebook uid.'))
            
            self.fb_session, created = FacebookSession.objects.get_or_create(
              uid=facebook_uid,
              defaults={
                'access_token': facebook_access_token, 
                'expires': datetime.datetime.now() + datetime.timedelta(seconds=facebook_expires)
            })

            if self.me.get('email', None):
                self.cleaned_data['email'] = self.me['email']
            else:
                raise forms.ValidationError(_("Les serveurs de Facebook sont inaccessibles. Veuillez reessayer dans quelques secondes."))
            
            if not created:
                # if already existed because of registered user or started facebook registration process,
                # we refresh login information
                self.fb_session.access_token = facebook_access_token
                self.fb_session.expires = datetime.datetime.now() + datetime.timedelta(seconds=facebook_expires)
                self.fb_session.save()
            
            if self.fb_session.user:
                self.user_cache = self.fb_session.user
            else:
                try:
                    self.user_cache = Patron.objects.get(email=self.me['email'])
                    self.fb_session.user = self.user_cache
                    self.fb_session.save()
                except Patron.DoesNotExist:
                    pass

        else:
            email = self.cleaned_data.get('email')
            
            if email is None or email == u'':
                raise forms.ValidationError('Empty email') # TODO: more meaningful error message
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


class CommentedCheckboxInput(forms.CheckboxInput):

    def __init__(self, info_text, attrs=None, check_test=bool):
        super(CommentedCheckboxInput, self).__init__(attrs, check_test)
        from django.utils.html import escape
        self.info_text = escape(_(info_text))

    def render(self, name, value, attrs=None):
        from django.utils.safestring import mark_safe
        print 'hello'
        return mark_safe('<label class="checkbox">' + super(CommentedCheckboxInput, self).render(name, value, attrs) + '\t' + self.info_text + '</label>')


class PatronEditForm(forms.ModelForm):
    is_professional = forms.BooleanField(label=_(u"Professionnel"), required=False, initial=False, widget=CommentedCheckboxInput(info_text='Je suis professionnel'))
    company_name = forms.CharField(label=_(u"Nom de la société"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}))
    
    email = forms.EmailField(label=_(u"Email"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    username = forms.RegexField(label=_(u"Pseudo"), max_length=30, regex=r'^[\w.@+-]+$',
    help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
    error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
    widget=forms.TextInput(attrs={'class': 'inm'}))
    
    first_name = forms.CharField(label=_(u"Prénom"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    last_name = forms.CharField(label=_(u"Nom"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    avatar = forms.ImageField(required=False)
    
    paypal_email = forms.EmailField(label=_(u"Email PayPal"), required=False, max_length=75, widget=forms.TextInput(attrs={
            'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
	
    work = forms.CharField(label=_(u"Travail"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}))
    school = forms.CharField(label=_(u"Etudes"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}))

    #is_professional = forms.BooleanField(label=_(u"Professionnel"), required=False, initial=False)
    
    is_subscribed = forms.BooleanField(required=False, initial=False, label=_(u"Newsletter"))
    new_messages_alerted = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(PatronEditForm, self).__init__(*args, **kwargs)
        self.fields['civility'].widget.attrs['class'] = "selm"
        self.fields['default_address'].widget.attrs['class'] = "selm"
        self.fields['default_address'].queryset = self.instance.addresses.all()
        print self.fields['is_professional'].widget

    class Meta:
        model = Patron
        fields = [
             'is_professional',
             'company_name',
             'username',
             'email',
             'civility',
             'first_name',
             'last_name',
             'avatar',
             'default_address',
             'paypal_email',
             'is_subscribed',
             'new_messages_alerted',
             'about',
             'school',
             'hobby',
             'work',
             'languages',
        ]
        widgets = {
            'is_professional': CommentedCheckboxInput('Je suis professionel'),
        }

    def save(self, *args, **kwargs):
        inst = super(PatronEditForm, self).save(*args, **kwargs)
        if self.avatar:
            try:
                self.instance.avatar.delete()
            except Avatar.DoesNotExist:
                pass
            Avatar.objects.create(image=self.avatar, patron=self.instance)
        return inst
    
    def clean_avatar(self):
        self.avatar = self.cleaned_data['avatar']
        return self.avatar
    
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
            is_verified = paypal_payment.verify_paypal_account(
                        email=paypal_email,
                        first_name=first_name,
                        last_name=last_name
                       )
            if is_verified == 'INVALID':
                form_errors_append(self, 'paypal_email', _(u"Vérifier qu'il s'agit bien de votre email PayPal"))
                form_errors_append(self, 'first_name', _(u"Vérifier que le prénom est identique à celui de votre compte PayPal"))
                form_errors_append(self, 'last_name', _(u"Vérifier que le nom est identique à celui de votre compte PayPal"))
            if not paypal_payment.confirm_paypal_account(email=paypal_email):
                form_errors_append(self, 'paypal_email', _(u"Vérifiez que vous avez bien répondu à l'email d'activation de Paypal"))
        return self.cleaned_data

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
            
class PatronPasswordChangeForm(PatronSetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'inm'}))
    
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
PatronPasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']
    

class PatronChangeForm(forms.ModelForm):
    class Meta:
        model = Patron
    

class PatronPaypalForm(forms.ModelForm):
    paypal_email = forms.EmailField(required=False, label=_("E-mail"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    paypal_exists = forms.TypedChoiceField(required=True, coerce=int, choices=PAYPAL_ACCOUNT_CHOICES, widget=forms.RadioSelect(renderer=ParagraphRadioFieldRenderer), initial=1)
    
    def clean(self):
        paypal_email = self.cleaned_data.get('paypal_email', None)
        self.paypal_exists = self.cleaned_data['paypal_exists']
        if not paypal_email:
            if self.paypal_exists:
                raise forms.ValidationError(_(u"Vous devez entrer votre email Paypal"))
            else:
                self.cleaned_data['paypal_email'] = self.instance.email
        return self.cleaned_data
    
    class Meta:
        model = Patron
        fields = ('paypal_email',)
    

class PhoneNumberForm(forms.ModelForm):
    number = PhoneNumberField(label=_(u"Téléphone"), widget=forms.TextInput(attrs={'class': 'inm'}), required=False)

    def clean_number(self):
        if not self.cleaned_data['number']:
            raise forms.ValidationError(_(u"Vous devez spécifiez un numéro de téléphone"))
        return self.cleaned_data['number']
    
    class Meta:
        model = PhoneNumber
        exclude = ('patron')

class PhoneNumberBaseFormSet(BaseInlineFormSet):
    def clean(self):
        super(PhoneNumberBaseFormSet, self).clean()
        if not len(filter(lambda form:(not form.cleaned_data.get('DELETE', True) if hasattr(form, 'cleaned_data') else False), self.forms)):
            raise forms.ValidationError(_(u"Vous ne pouvez pas supprimer tout vos numéros."))
        if any(self.errors):
            return
        return self.cleaned_data

PhoneNumberFormset = inlineformset_factory(Patron, PhoneNumber, form=PhoneNumberForm, formset=PhoneNumberBaseFormSet, exclude=['kind'], extra=1, can_delete=True)

class AddressForm(forms.ModelForm):

    def clean(self):
        if self.instance.products.all() and self.cleaned_data['DELETE']:
            raise forms.ValidationError(_(u'Vous ne pouvez pas supprimer une adresse associé à un produit. Veuillez le changer sur le page produit.'))
        if self.cleaned_data['DELETE'] and self.instance.patron.default_address == self.instance:
            raise forms.ValidationError(_(u'Vous ne pouvez pas supprimer votre adresse par default.'))
        return self.cleaned_data

    class Meta:
        model = Address
        exclude = ('address2', 'position', 'objects', 'patron')
        widgets = {
            'address1': forms.Textarea(
                attrs={'class': 'inm street', 'placeholder': _(u'Rue')}
            ),
            'zipcode': forms.TextInput(
                attrs={'class': 'inm zipcode', 'placeholder': _(u'Code postal')}
            ),
            'city': forms.TextInput(
                attrs={'class': 'inm town', 'placeholder': _(u'Ville')}
            ),
            'country': forms.Select(
                attrs={'class': 'selm'}
            ),
        }

class AddressBaseFormSet(BaseInlineFormSet):

    def clean(self):
        super(AddressBaseFormSet, self).clean()
        if any(self.errors):
            raise forms.ValidationError('')
        for form in self.forms:
            pass
    
AddressFormSet = inlineformset_factory(Patron, Address, form=AddressForm, formset=AddressBaseFormSet, extra=1, can_delete=True)

def make_missing_data_form(instance, required_fields=[]):
    fields = SortedDict({
        'username': forms.RegexField(label=_(u"Pseudo"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
            widget=forms.TextInput(attrs={'class': 'inm'})
        ),
        'password1': forms.CharField(label=_(u"Mot de passe"), max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'inm'})),
        'password2': forms.CharField(label=_(u"A nouveau"), max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'inm'})),
        'is_professional': forms.BooleanField(label=_(u"Professionnel"), required=False, initial=False),
        'company_name': forms.CharField(label=_(u"Nom de la société"), required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'inm'})),
        'first_name': forms.CharField(label=_(u"Prénom"), max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'last_name': forms.CharField(label=_(u"Nom"), max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'inm'})),
        'addresses__address1': forms.CharField(max_length=255, widget=forms.Textarea(attrs={'class': 'inm street', 'placeholder': _(u'Rue')})),
        'addresses__zipcode': forms.CharField(required=True, max_length=9, widget=forms.TextInput(attrs={
            'class': 'inm zipcode', 'placeholder': _(u'Code postal')
        })),
        'addresses__city': forms.CharField(required=True, max_length=255, widget=forms.TextInput(attrs={'class': 'inm town', 'placeholder': _(u'Ville')})),
        'addresses__country': forms.ChoiceField(choices=COUNTRY_CHOICES, required=True, widget=forms.Select(attrs={'class': 'selm'})),
        'avatar': forms.ImageField(required=False),
        'phones__phone': PhoneNumberField(label=_(u"Téléphone"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    })

    # Do we have an address ?
    if instance and instance.addresses.exists():
        fields['addresses'] = forms.ModelChoiceField(label=_(u"Addresse"), required=False,
            queryset=instance.addresses.all(), initial=instance.default_address if instance.default_address else instance.addresses.all()[0], widget=forms.Select(attrs={'class': 'selm'}))
        for f in fields.keys():
            if "addresses" in f:
                fields[f].required = False
    
    # Do we have a phone number ?
    if instance and instance.phones.exists():
        fields['phones'] = forms.ModelChoiceField(label=_(u"Téléphone"), required=False, 
            queryset=instance.phones.all(), initial=instance.phones.all()[0], widget=forms.Select(attrs={'class': 'selm'}))
        if fields.has_key('phones__phone'):
            fields['phones__phone'].required = False
    
    # Do we have a password ?
    if fields.has_key('password1'):
        if instance and getattr(instance, 'password', None):
            del fields['password1']
            del fields['password2']
    
    if instance and instance.username and "first_name" not in required_fields:
        del fields['avatar']

    # Are we in presence of a pro ?
    if fields.has_key('is_professional'):
        if instance and getattr(instance, 'is_professional', None)!=None:
            del fields['is_professional']
            del fields['company_name']
            
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
            if "addresses" not in attr and "phones" not in attr and "avatar" not in attr: # wtf is this checking?
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
        self.instance.save()
        avatar = None
        if hasattr(self, 'avatar') and self.avatar:
            avatar = Avatar.objects.create(image=self.avatar, patron=self.instance)
        return self.instance, address, phone, avatar
    
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
    
    def clean_avatar(self):
        self.avatar = self.cleaned_data.get('avatar', None)
        return self.avatar
    
    form_class = type('MissingInformationForm', (forms.BaseForm,), {'instance': instance, 'base_fields': fields})
    form_class.save = types.MethodType(save, None, form_class)
    form_class.clean_password2 = types.MethodType(clean_password2, None, form_class)
    form_class.clean_username = types.MethodType(clean_username, None, form_class)
    form_class.clean_phones = types.MethodType(clean_phones, None, form_class)
    form_class.clean_addresses = types.MethodType(clean_addresses, None, form_class)
    form_class.clean_company_name = types.MethodType(clean_company_name, None, form_class)
    form_class.clean_avatar = types.MethodType(clean_avatar, None, form_class)
    return fields != {}, form_class

class ContactForm(forms.Form):
    subject = forms.CharField(label=_(u"Sujet"), max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    message = forms.CharField(label=_(u"Message"), required=True, widget=forms.Textarea(attrs={'class': 'inm'}))
    sender = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'
    }))
    cc_myself = forms.BooleanField(label=_(u"Je souhaite recevoir une copie de ce message."), required=False)
