# -*- coding: utf-8 -*-
import types
import re
import datetime

from django import forms
from form_utils.forms import BetterForm, BetterModelForm
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import is_password_usable
from django.contrib.sites.models import Site, get_current_site
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.forms.fields import EMPTY_VALUES
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext as _
from django.forms.formsets import ORDERING_FIELD_NAME, DELETION_FIELD_NAME
import facebook

from accounts import EMAIL_BLACKLIST
from accounts.fields import PhoneNumberField, ExpirationField, RIBField, DateSelectField, CreditCardField
from accounts.models import Patron, PhoneNumber, CreditCard, FacebookSession, Address, Language, OpeningTimes, IDNSession
from accounts.choices import COUNTRY_CHOICES, STATE_CHOICES, PAYPAL_ACCOUNT_CHOICES
from accounts.widgets import ParagraphRadioFieldRenderer, CommentedCheckboxInput
from payments.paybox_payment import PayboxManager, PayboxException

from eloue import legacy

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
    exists = legacy.TypedChoiceField(required=True, coerce=int, choices=STATE_CHOICES, widget=forms.RadioSelect(renderer=ParagraphRadioFieldRenderer), initial=1)
    email = forms.EmailField(label=_(u"Email"), max_length=75, required=False, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm', 'tabindex': '1', 'placeholder': _(u"Email")
    }))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(attrs={'placeholder': _(u"Mot de passe"), 'tabindex': '2'}), required=False)
    
    # for facebook connect
    facebook_access_token = forms.CharField(required=False, widget=forms.HiddenInput())
    facebook_expires = forms.IntegerField(required=False, widget=forms.HiddenInput())
    facebook_uid = forms.CharField(required=False, widget=forms.HiddenInput())

    idn_oauth_verifier = forms.CharField(required=False, widget=forms.HiddenInput())
    idn_id = forms.CharField(required=False, widget=forms.HiddenInput())
    idn_access_token = forms.CharField(required=False, widget=forms.HiddenInput())

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
                raise forms.ValidationError(_(u"Pour garantir un service de qualité et la sécurité des utilisateurs d'e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
        
        if not exists and Patron.objects.filter(email=email).exists():
            raise forms.ValidationError(_(u"Un compte existe déjà pour cet email"))
        
        return email

    def clean(self):
        facebook_access_token = self.cleaned_data.get('facebook_access_token')
        facebook_expires = self.cleaned_data.get('facebook_expires')
        facebook_uid = self.cleaned_data.get('facebook_uid')

        idn_id = self.cleaned_data.get('idn_id')
        idn_access_token = self.cleaned_data.get('idn_access_token')

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if any([facebook_access_token, facebook_expires, facebook_uid]) and not any([email, password]):
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

        elif any([idn_access_token, idn_id]):
            import oauth2 as oauth
            import urllib, urlparse
            from django.core.urlresolvers import reverse
            import pprint, simplejson
            consumer_key = '_ce85bad96eed75f0f7faa8f04a48feedd56b4dcb'
            consumer_secret = '_80b312627bf936e6f20510232cf946fff885d1f7'
            base_url = 'http://idn.recette.laposte.france-sso.fr/'
            request_token_url = base_url + 'oauth/requestToken'
            authorize_url = base_url + 'oauth/authorize'
            access_token_url = base_url + 'oauth/accessToken'
            try:
                access_token_data = self.request.session[(idn_id, idn_access_token)]
            except KeyError:
                self.request.session.pop('idn_info', None)
                raise forms.ValidationError('Activate cookies')

            # We kept here the fb_session variable name, though we should change it to something
            # more general, like self.oauth_session. In order to do that, we need to change it
            # in the previous if block, in the wizard and possibly in some template too.
            self.fb_session, created = IDNSession.objects.get_or_create(
                uid=idn_id, defaults = {
                    'access_token': access_token_data['oauth_token'],
                    'access_token_secret': access_token_data['oauth_token_secret']
                }
            )
            if not created:
                self.fb_session.access_token = access_token_data['oauth_token']
                self.fb_session.access_token_secret = access_token_data['oauth_token_secret']
                self.fb_session.save()

            self.me = self.fb_session.me
            
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
            if email is None or email == u'':
                raise forms.ValidationError('Empty email') # TODO: more meaningful error message
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

class PatronEditForm(BetterModelForm):
    is_professional = forms.BooleanField(label=_(u"Professionnel"), required=False, initial=False, widget=CommentedCheckboxInput(info_text='Je suis professionnel'))
    company_name = forms.CharField(label=_(u"Nom de la société"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}))
    
    email = forms.EmailField(label=_(u"Email"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    username = forms.RegexField(label=_(u"Pseudo"), max_length=30, regex=r'^[\w.@+-]+$',
    help_text=_(u"Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
    error_messages={'invalid': _(u"This value may contain only letters, numbers and @/./+/-/_ characters.")},
    widget=forms.TextInput(attrs={'class': 'inm'}))
    
    first_name = forms.CharField(label=_(u"Prénom"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    last_name = forms.CharField(label=_(u"Nom"), required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    avatar = forms.ImageField(required=False, label=_(u"Photo de profil"))
    

    is_subscribed = forms.BooleanField(required=False, initial=False, label=_(u"Newsletter"), widget=CommentedCheckboxInput(info_text="J'accepte de recevoir de recevoir la Newsletter de e-loue"))
    new_messages_alerted = forms.BooleanField(label=_(u"Notifications"), required=False, initial=True, widget=CommentedCheckboxInput(info_text="J'accepte de recevoir les messages des autres membres"))

    date_of_birth = DateSelectField(required=False, label=_(u"Lieu de naissance"))
    drivers_license_date = DateSelectField(required=False, label=_(u"Date d'obtention"))

    about = forms.CharField(label=_(u"A propos de vous"), required=False, widget=forms.Textarea(attrs={'class': 'inm'}))
    work = forms.CharField(label=_(u"Travail"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}), help_text=_(u"Exemple : Directrice Resources Humaines, ma socitée"))
    school = forms.CharField(label=_(u"Etudes"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}), help_text=_(u"Exemple : Université Panthéon Sorbonne (Paris I)"))
    hobby = forms.CharField(label=_(u"Hobbies"), required=False, widget=forms.TextInput(attrs={'class': 'inm'}))
    languages = forms.ModelMultipleChoiceField(queryset=Language.objects, label=_(u"Langues parlées"), required=False, widget=forms.SelectMultiple(attrs={'data-placeholder': _(u'Choisissez vos langues')}) )

    class Meta:
        model = Patron
        fieldsets = [
            ('basic_info', {
                'fields': [
                    'is_professional', 'company_name', 'username', 'avatar', 
                    'email', 'civility', 'first_name', 'last_name',
                    'default_address', 'default_number', 'date_of_birth', 'place_of_birth',
                    'is_subscribed', 'new_messages_alerted',
                ],
                'legend': _(u'Informations nécessaires')
            }),
            ('extra_info', {
                'fields': ['about', 'work', 'school', 'hobby', 'languages'],
                'legend': _(u"Informations de profil")
            }),
            ('driver_info', {
                'fields': ['drivers_license_date', 'drivers_license_number'],
                'legend': _(u"Informations sur le permis")
            })
        ]
        widgets = {
            'is_professional': CommentedCheckboxInput('Je suis professionel'),
        }

    def __init__(self, *args, **kwargs):
        super(PatronEditForm, self).__init__(*args, **kwargs)
        self.legend = _(u"Informations nécessaires")
        self.fields['civility'].widget.attrs['class'] = "selm"
        self.fields['default_address'].widget.attrs['class'] = "selm"
        self.fields['default_address'].label = _(u'Adresse par defaut')
        self.fields['default_address'].queryset = self.instance.addresses.all()
        self.fields['default_number'].widget.attrs['class'] = "selm"
        self.fields['default_number'].label = _(u'Téléphone par defaut')
        self.fields['default_number'].queryset = self.instance.phones.all()
    
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
                raise forms.ValidationError(_(u"Pour garantir un service de qualité et la sécurité des utilisateurs d'e-loue.com dans le métro, vous ne pouvez pas vous enregistrer avec une adresse email jetable. Ne craignez rien, vous ne recevrez aucun courrier indésirable."))
        try:
            Patron.objects.exclude(pk=self.instance.pk).get(email=email)
            raise forms.ValidationError(_(u"Un compte avec cet email existe déjà"))
        except Patron.DoesNotExist:
            return email
    
    def clean(self):
        first_name = self.cleaned_data.get('first_name', None)
        last_name = self.cleaned_data.get('last_name', None)
        
        return self.cleaned_data

from accounts.models import ProPackage
from django.db.models import Q
class CompanyEditForm(PatronEditForm):
    avatar = forms.ImageField(required=False, label=_(u"Logo de l\'entreprise"))
    about = forms.CharField(label=_(u"A propos de l'entreprise"), required=False, widget=forms.Textarea(), help_text=_(u'Décrivez votre entreprise afin d’expliquer aux membres de e-loue votre activité.'))

    class Meta:
        model = Patron
        fieldsets = [
            ('basic_info', {
                'fields': [
                    'is_professional', 'company_name', 'username', 'avatar', 
                    'email', 'civility', 'first_name', 'last_name',
                    'default_address', 'default_number', 'date_of_birth', 'place_of_birth', 'is_subscribed', 'new_messages_alerted',
                ],
                'legend': _(u'Informations nécessaires')
            }),
            ('extra_info', {
                'fields': ['about', 'url', 'languages'],
                'legend': _(u"Informations sur l'entreprise")
            }),
            ('driver_info', {
                'fields': ['drivers_license_date', 'drivers_license_number'],
                'legend': _(u"Informations sur le permis")
            })
        ]
        widgets = {
            'is_professional': CommentedCheckboxInput('Je suis professionel'),
        }

    def __init__(self, *args, **kwargs):
        super(PatronEditForm, self).__init__(*args, **kwargs)
        self.fields['default_address'].label = _(u'Adresse de l\'entreprise')
        self.fields['default_address'].queryset = self.instance.addresses.all()
        self.fields['default_number'].label = _(u'Téléphone de l\'entreprise')
        self.fields['default_number'].queryset = self.instance.phones.all()


class SubscriptionEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SubscriptionEditForm, self).__init__(*args, **kwargs)
        now = datetime.datetime.now()
        self.fields['subscription'] = forms.ModelChoiceField(required=True,
            queryset=ProPackage.objects.filter(
                Q(valid_until__isnull=True)|Q(valid_until__lte=now) 
            )
        )


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
    old_password = forms.CharField(label=_(u"Ancien mot de passe"), widget=forms.PasswordInput(attrs={'class': 'inm'}))
    
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
    

class PatronPaypalForm(forms.ModelForm):
    paypal_email = forms.EmailField(required=False, label=_("E-mail"), max_length=75, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'}))
    paypal_exists = legacy.TypedChoiceField(required=True, coerce=int, choices=PAYPAL_ACCOUNT_CHOICES, widget=forms.RadioSelect(renderer=ParagraphRadioFieldRenderer), initial=1)
    
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

    def clean(self):
        if self.cleaned_data.get('DELETE', False) and self.instance.patron.default_number == self.instance:
            raise forms.ValidationError(_(u'Vous ne pouvez pas supprimer votre numéro par default.'))
        return self.cleaned_data

    class Meta:
        model = PhoneNumber
        fields = ('number', )

class MixinHiddenDeleteFormset(object):
    # mixin to hide delete and order fields for the extra fields for the formset
    def add_fields(self, form, index):
        if index < self.initial_form_count():
            return super(MixinHiddenDeleteFormset, self).add_fields(form, index)
        if self.can_order:
            # Only pre-fill the ordering field for initial forms.
            if index is not None and index < self.initial_form_count():
                form.fields[ORDERING_FIELD_NAME] = forms.IntegerField(label=_(u'Order'), initial=index+1, required=False, widget=forms.HiddenInput())
            else:
                form.fields[ORDERING_FIELD_NAME] = forms.IntegerField(label=_(u'Order'), required=False, widget=forms.HiddenInput())
        if self.can_delete:
            form.fields[DELETION_FIELD_NAME] = forms.BooleanField(label=_(u'Delete'), required=False, widget=forms.HiddenInput())
        


class PhoneNumberBaseFormSet(MixinHiddenDeleteFormset, BaseInlineFormSet):
    def clean(self):
        super(PhoneNumberBaseFormSet, self).clean()
        if not len(filter(lambda form:(not form.cleaned_data.get('DELETE', True) if hasattr(form, 'cleaned_data') else False), self.forms)):
            raise forms.ValidationError(_(u"Vous ne pouvez pas supprimer tous vos numéros."))
        if any(self.errors):
            raise forms.ValidationError('')
        return self.cleaned_data

PhoneNumberFormset = inlineformset_factory(Patron, PhoneNumber, form=PhoneNumberForm, formset=PhoneNumberBaseFormSet, exclude=['kind'], extra=1, can_delete=True)

class AddressForm(forms.ModelForm):
    address1 = forms.CharField(label=_(u"Adresse"), widget=forms.Textarea(attrs={'class': 'inm street', 'placeholder': _(u'Rue')}))
    zipcode = forms.CharField(label=_(u"Code Postal"), widget=forms.TextInput(attrs={'class': 'inm zipcode', 'placeholder': _(u'Code postal')}))
    city = forms.CharField(label=_(u"Ville"), widget=forms.TextInput(attrs={'class': 'inm town', 'placeholder': _(u'Ville')}))

    def clean(self):
        if self.instance.products.all() and self.cleaned_data['DELETE']:
            raise forms.ValidationError(_(u'Vous ne pouvez pas supprimer une adresse associé à un produit. Veuillez le changer sur le page produit.'))
        if self.cleaned_data['DELETE'] and self.instance.patron.default_address == self.instance:
            raise forms.ValidationError(_(u'Vous ne pouvez pas supprimer votre adresse par default.'))
        return self.cleaned_data

    class Meta:
        model = Address
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
        fields = [
            'address1',
            'zipcode',
            'city',
            'country',
        ]

class AddressBaseFormSet(MixinHiddenDeleteFormset, BaseInlineFormSet):
    def clean(self):
        super(AddressBaseFormSet, self).clean()
        if any(self.errors):
            raise forms.ValidationError('')
        for form in self.forms:
            pass
    

AddressFormSet = inlineformset_factory(Patron, Address, form=AddressForm, formset=AddressBaseFormSet, extra=1, can_delete=True)

class RIBForm(forms.ModelForm):
    
    rib = RIBField(label='RIB')

    class Meta:
        model = Patron
        fields = ('rib', )


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
        if self.errors:
            return self.cleaned_data
        try:
            from payments.paybox_payment import PayboxManager, PayboxException
            pm = PayboxManager()
            self.cleaned_data['masked_number'] = mask_card_number(self.cleaned_data['card_number'])
            pm.authorize(self.cleaned_data['card_number'], 
                self.cleaned_data['expires'], self.cleaned_data['cvv'], 1, 'verification'
            )
        except PayboxException as e:
            raise forms.ValidationError(_(u'La validation de votre carte a échoué.'))
        return self.cleaned_data

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        pm = PayboxManager()
        try:
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
        except PayboxException:
            raise
        instance = super(CreditCardForm, self).save(*args, commit=False, **kwargs)
        instance.card_number = self.cleaned_data['card_number']
        instance.masked_number = self.cleaned_data['masked_number']
        if commit:
            instance.save()
        return instance

class BookingCreditCardForm(CreditCardForm):
    class Meta(CreditCardForm.Meta):
        # see note: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#using-a-subset-of-fields-on-the-form
        # we excluded, then added, to avoid save automatically the card_number
        exclude = ('card_number', 'holder', 'masked_number')

class ExistingBookingCreditCardForm(CreditCardForm):
    cvv = forms.CharField(max_length=4, required=False, label=_(u'Cryptogramme de sécurité'), help_text=_(u'Les 3 derniers chiffres au dos de la carte.'))
    expires = ExpirationField(label=_(u'Date d\'expiration'), required=False)

    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)
        self.fields['card_number'] = forms.CharField(
            label=_(u'Numéro de carte de crédit'),
            min_length=16, max_length=24, required=False
        )
        self.fields['holder_name'] = forms.CharField(
            label=_(u'Titulaire de la carte'), required=False
        )

    def clean(self):
        if self.errors:
            return self.cleaned_data
        cvv = self.cleaned_data.get('cvv')
        holder_name = self.cleaned_data.get('holder_name')
        card_number = self.cleaned_data.get('card_number')
        expires = self.cleaned_data.get('expires')
        if any((cvv, holder_name, card_number, expires)):
            if not all((cvv, holder_name, card_number, expires)):
                raise forms.ValidationError('You have to fill out all the fields')
            else:
                try:
                    from payments.paybox_payment import PayboxManager, PayboxException
                    pm = PayboxManager()
                    self.cleaned_data['masked_number'] = mask_card_number(self.cleaned_data['card_number'])
                    pm.authorize(self.cleaned_data['card_number'], 
                        self.cleaned_data['expires'], self.cleaned_data['cvv'], 1, 'verification'
                    )
                except PayboxException as e:
                    raise forms.ValidationError(_(u'La validation de votre carte a échoué.'))
        return self.cleaned_data

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        cvv = self.cleaned_data.get('cvv')
        holder_name = self.cleaned_data.get('holder_name')
        card_number = self.cleaned_data.get('card_number')
        expires = self.cleaned_data.get('expires')
        if any((cvv, holder_name, card_number, expires)):
            pm = PayboxManager()
            try:
                self.cleaned_data['card_number'] = pm.modify(
                    self.instance.subscriber_reference, 
                    self.cleaned_data['card_number'],
                    self.cleaned_data['expires'], self.cleaned_data['cvv']) 
            except PayboxException:
                raise
            instance = super(CreditCardForm, self).save(*args, commit=False, **kwargs)
            instance.card_number = self.cleaned_data['card_number']
            instance.masked_number = self.cleaned_data['masked_number']
            if commit:
                instance.save()
            return instance
        return self.instance

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
            from payments.paybox_payment import PayboxManager, PayboxException
            import uuid
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
                from payments.paybox_payment import PayboxManager, PayboxException
                pm = PayboxManager()
                self.cleaned_data['masked_number'] = mask_card_number(self.cleaned_data['card_number'])
                pm.authorize(self.cleaned_data['card_number'], 
                    self.cleaned_data['expires'], self.cleaned_data['cvv'], 1, 'verification'
                )
            except PayboxException as e:
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


class ContactForm(forms.Form):
    sender = forms.EmailField(label=_(u"Email"), max_length=75, required=True, widget=forms.TextInput(attrs={
        'autocapitalize': 'off', 'autocorrect': 'off', 'class': 'inm'
    }))
    subject = forms.CharField(label=_(u"Sujet"), max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'inm'}))
    message = forms.CharField(label=_(u"Message"), required=True, widget=forms.Textarea(attrs={'class': 'inm'}))
    cc_myself = forms.BooleanField(label=_(u"Etre en copie"), required=False)


class OpeningsForm(BetterModelForm):

    def clean(self):
        cleaned_data = super(OpeningsForm, self).clean()
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            opens_var = day + '_opens'
            closes_var = day + '_closes'
            opens_second_var = day + '_opens_second'
            closes_second_var = day + '_closes_second'

            opens = cleaned_data.get(opens_var)
            closes = cleaned_data.get(closes_var)
            opens_second = cleaned_data.get(opens_second_var)
            closes_second = cleaned_data.get(closes_second_var)
            if opens and closes:
                # we are open the given day
                if opens >= closes:
                    # so the opening time should preced closing time
                    error_msg = _(u'L\'heure d\'ouverture doit etre inferieure a celui de fermeture')
                    self._errors[opens_var] = error_msg
                    self._errors[closes_var] = error_msg
                    cleaned_data.pop(opens_var, None)
                    cleaned_data.pop(closes_var, None)
                if opens_second and closes_second:
                    # if there is a pause
                    if not opens < closes < opens_second < closes_second:
                        error_msg = _(u'Le debut de la tranche horaire doit précéder la fin')
                        self._errors[opens_var] = error_msg
                        self._errors[closes_var] = error_msg
                        self._errors[opens_second_var] = error_msg
                        self._errors[closes_second_var] = error_msg
                        cleaned_data.pop(opens_var, None)
                        cleaned_data.pop(closes_var, None)
                        cleaned_data.pop(opens_second_var, None)
                        cleaned_data.pop(closes_second_var, None)
                elif opens_second or closes_second:
                    error_msg = _(u'Vous devez saisir le debut et la fin de la tranche d\'horaire')
                    self._errors[opens_second_var] = error_msg
                    self._errors[closes_second_var] = error_msg
                    cleaned_data.pop(opens_second_var, None)
                    cleaned_data.pop(closes_second_var, None)
            elif not opens and not closes:
                # we are not open
                if opens_second or closes_second:
                    error_msg = _(u'Vous ne pouvez pas definir de tranche horaire si vous n\'etes pas ouvert')
                    self._errors[opens_second_var] = error_msg
                    self._errors[closes_second_var] = error_msg
                    cleaned_data.pop(opens_second_var, None)
                    cleaned_data.pop(closes_second_var, None)
            else:
                # errounous
                error_msg = _(u'Vous devez saisir l\'ouverture et le fermeture')
                self._errors[opens_var] = error_msg
                self._errors[closes_var] = error_msg
                cleaned_data.pop(opens_var, None)
                cleaned_data.pop(closes_var, None)
        return cleaned_data

    class Meta:
        model = OpeningTimes
        fieldsets = [
            ('monday', {
                'fields': ['monday_opens', 'monday_closes', 'monday_opens_second', 'monday_closes_second', ],
                'legend': _('Lundi'),
                }),
            ('tuesday', {
                'fields': ['tuesday_opens', 'tuesday_closes', 'tuesday_opens_second', 'tuesday_closes_second',],
                'legend': _('Mardi'),
                }),
            ('wednesday', {
                'fields': ['wednesday_opens', 'wednesday_closes', 'wednesday_opens_second', 'wednesday_closes_second',],
                'legend': _('Mercredi'),
                }),
            ('thursday', {
                'fields': ['thursday_opens', 'thursday_closes', 'thursday_opens_second', 'thursday_closes_second',],
                'legend': _('Jeudi'),
                }),
            ('friday', {
                'fields': ['friday_opens', 'friday_closes', 'friday_opens_second', 'friday_closes_second', ],
                'legend': _('Vendredi'),
                }),
            ('saturday', {
                'fields': ['saturday_opens', 'saturday_closes', 'saturday_opens_second', 'saturday_closes_second',],
                'legend': _('Samedi'),
                }),
            ('sunday', {
                'fields': ['sunday_opens', 'sunday_closes', 'sunday_opens_second', 'sunday_closes_second',],
                'legend': _('Dimanche'),
                }),
        ]

class GmailContactForm(forms.Form):
    checked = forms.BooleanField(required=False)
    name = forms.CharField(max_length=200, required=False, widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.HiddenInput())

class BaseGmailContactFormset(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return self.cleaned_data
        checked_contacts = filter(lambda form: form.cleaned_data.get('checked', None), self.forms)
        if len(checked_contacts) > 20:
            raise forms.ValidationError(_('Vous pouvez choisir 20 contacts maximum'))
        return self.cleaned_data

GmailContactFormset = formset_factory(GmailContactForm, formset=BaseGmailContactFormset, extra=0)
