# -*- coding: utf-8 -*-
try:
    import cPickle as pickle
except ImportError:
    import pickle

import itertools

from urllib2 import urlopen
import facebook
import django.forms as forms
from django.conf import settings
from django.contrib.formtools.wizard import FormWizard
from django.contrib.auth import login, authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.hashcompat import md5_constructor
from django.views.decorators.csrf import csrf_protect

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron, Avatar, FacebookSession
from eloue.geocoder import GoogleGeocoder

def isMissingInformationForm(obj):
    return getattr(obj.__class__, '__name__', None) == 'MissingInformationForm'

class MultiPartFormWizard(FormWizard):

    def __init__(self, *args, **kwargs):
        super(MultiPartFormWizard, self).__init__(*args, **kwargs)
        self.required_fields = [
          'username', 'password1', 'password2', 'is_professional', 'company_name', 'first_name', 'last_name',
          'phones', 'phones__phone', 'addresses',
          'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country', 'avatar'
        ]
        self.fb_session = None
        self.new_patron = None
        self.me = {}
    
    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self.patron = request.user
            if not self.fb_session:
                try:
                    self.fb_session = self.patron.facebooksession
                    self.me = self.fb_session.me
                except (FacebookSession.DoesNotExist, facebook.GraphAPIError):
                    pass
            if EmailAuthenticationForm in self.form_list and len(self.form_list) > 1:
                self.form_list.remove(EmailAuthenticationForm)
            if not any(map(lambda el: getattr(el, '__name__', None) == 'MissingInformationForm', self.form_list)):
                missing_fields, missing_form = make_missing_data_form(request.user, self.required_fields)
                if missing_fields:
                    self.form_list.insert(1, missing_form)
        else:
            if EmailAuthenticationForm not in self.form_list:
                self.form_list.append(EmailAuthenticationForm)
            if EmailAuthenticationForm in self.form_list:
                if not next((form for form in self.form_list if getattr(form, '__name__', None) == 'MissingInformationForm'), None):
                    form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                    form.is_valid()  # Here to fill form user_cache
                    if form.fb_session and 'password1' in self.required_fields:
                        self.required_fields.remove('password1')
                        self.required_fields.remove('password2')
                    missing_fields, missing_form = make_missing_data_form(form.get_user(), self.required_fields)
                    if missing_fields:
                        self.form_list.insert(2, missing_form)
        return super(MultiPartFormWizard, self).__call__(request, *args, **kwargs)

    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            if not self.new_patron:
                if self.fb_session:
                    self.new_patron = Patron.objects.create_user(
                      missing_form.cleaned_data['username'], 
                      auth_form.cleaned_data['email']
                    )
                    self.fb_session.user = self.new_patron
                    self.fb_session.save()
                else:
                    self.new_patron = Patron.objects.create_inactive(
                      missing_form.cleaned_data['username'],
                      auth_form.cleaned_data['email'], 
                      missing_form.cleaned_data['password1']
                    )
                if hasattr(settings, 'AFFILIATE_TAG'):
                    # Assign affiliate tag, no need to save, since missing_form should do it for us
                    self.new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(self.new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                self.new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, self.new_patron)
        else:
            self.new_patron = request.user

        if missing_form:
            missing_form.instance = self.new_patron
            self.new_patron, self.new_address, self.new_phone, avatar = missing_form.save()
            if not avatar and self.fb_session:
                try:
                    self.new_patron.avatar
                except Avatar.DoesNotExist:
                    if 'picture' in self.me and 'static-ak' not in self.me['picture']:
                        try:
                            fb_image_object = urlopen(self.me['picture']).read()
                            Avatar(patron=self.new_patron, image=SimpleUploadedFile('picture',fb_image_object)).save()
                        except IOError:
                            pass
        address = None
        from eloue.accounts.views import GEOLOCATION_SOURCE
        if not request.session.get('location') or request.session['location'].get('source') > GEOLOCATION_SOURCE.ADDRESS:
            if self.new_patron.default_address and self.new_patron.default_address.is_geocoded():
                address = self.new_patron.default_address
            else:
                address = next(
                    itertools.ifilter(
                            lambda address: address.is_geocoded(), 
                            self.new_patron.addresses.all()
                    ), 
                    None
                )
            if address:
                request.session['location'] = {
                    'city': address.city,
                    'coordinates': address.position.coords,
                    'country': address.get_country_display(),
                    'fallback': None,
                    'radius': 5,
                    'region': None,
                    'region_coords': None,
                    'region_radius': None,
                    'source': GEOLOCATION_SOURCE.ADDRESS,
                }

    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if next_form.__name__ == 'MissingInformationForm':
            initial = {
                'addresses__country': settings.LANGUAGE_CODE.split('-')[1].upper(),
                'first_name': self.me.get('first_name', '') if self.me else '',
                'last_name': self.me.get('last_name', '') if self.me else '',
                'username': self.me.get('username', '') if self.me else '',
            }
            if self.me and 'location' in self.me:
                try:
                    if self.me['location']['name']:
                        city, country = GoogleGeocoder().getCityCountry(self.me['location']['name'])
                        initial['addresses__country'] = country
                        initial['addresses__city'] = city
                except (KeyError, IndexError):
                    pass
            
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial)
        else:
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step), initial=self.initial.get(step, None))
    
    def security_hash(self, request, form):
        data = []
        for bf in form:
            # Get the value from the form data. If the form allows empty or hasn't
            # changed then don't call clean() to avoid trigger validation errors
            if isinstance(bf.field, forms.FileField):
                continue
            if form.empty_permitted and not form.has_changed():
                value = bf.data or ''
            else:
                value = bf.field.clean(bf.data) or ''
            if isinstance(value, basestring):
                value = value.strip()
            data.append((bf.name, value))
        data.append(settings.SECRET_KEY)
        
        pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        return md5_constructor(pickled).hexdigest()
    
    def render(self, form, request, step, context={}):
        if form.__class__.__name__ == 'MissingInformationForm':
            # maybe we should move this section into process_step, or another function
            # this does not seem the best place to handle
            if self.fb_session:
                default_picture = settings.MEDIA_URL + 'images/default_avatar.png'
                context['fb_image'] = self.me.get('picture', default_picture)
        old_data, old_files = request.POST, request.FILES
        prev_fields = []
        if old_data:
            hidden = forms.HiddenInput()
            # Collect all data from previous steps and render it as HTML hidden fields.
            for i in range(step):
                old_form = self.get_form(i, old_data, old_files)
                hash_name = 'hash_%s' % i
                prev_fields.extend([bf.as_hidden() for bf in old_form])
                prev_fields.append(hidden.render(hash_name, old_data.get(hash_name, self.security_hash(request, old_form))))
        return self.render_template(request, form, ''.join(prev_fields), step, context)

    def process_step(self, request, form, step):
        super(MultiPartFormWizard, self).process_step(request, form, step)
        self.user = request.user
        if isinstance(form, EmailAuthenticationForm):
            self.fb_session = form.fb_session
            self.new_patron = form.get_user()
            self.me = form.me
        if self.fb_session and 'password1' in self.required_fields:
            self.required_fields.remove('password1')
            self.required_fields.remove('password2')

