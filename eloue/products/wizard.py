# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to, direct_to_template
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron, Avatar

from eloue.products.forms import AlertForm, ProductForm, MessageEditForm

from eloue.products.models import Product, Picture, UNIT, Alert

from eloue.wizard import GenericFormWizard
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template, redirect_to
from eloue.geocoder import GoogleGeocoder

class ProductWizard(GenericFormWizard):
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        if request.user.is_anonymous():  # Create new Patron
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
        else:
            new_patron = request.user
        
        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone, avatar = missing_form.save()
            if not avatar and fb_session:
                if 'picture' in self.me:
                    from urllib2 import urlopen
                    from django.core.files.uploadedfile import SimpleUploadedFile

                    fb_image_object = urlopen(self.me['picture']).read()
                    Avatar(patron=new_patron, image=SimpleUploadedFile('picture',fb_image_object)).save()
        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_address
        product = product_form.save()
        
        for unit in UNIT.keys():
            field = "%s_price" % unit.lower()
            if field in product_form.cleaned_data and product_form.cleaned_data[field]:
                product.prices.create(
                    unit=UNIT[unit],
                    amount=product_form.cleaned_data[field]
                )
        
        if product_form.cleaned_data.get('picture_id', None):
            product.pictures.add(Picture.objects.get(pk=product_form.cleaned_data['picture_id']))
        
        GoalRecord.record('new_object', WebUser(request))
        
        return redirect_to(request, product.get_absolute_url(), permanent=False)
    
    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if issubclass(next_form, ProductForm):
            if files and '0-picture' in files:  # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=Product(quantity=1, deposit_amount=0))
        elif next_form.__name__ == 'MissingInformationForm':
            #if not issubclass(next_form, (ProductForm, EmailAuthenticationForm)):
            initial = {
                'addresses__country': settings.LANGUAGE_CODE.split('-')[1].upper(),
                'first_name': self.me.get('first_name', '') if self.me else '',
                'last_name': self.me.get('last_name', '') if self.me else '',
                'username': self.me.get('username', '') if self.me else '',
            }
            if self.me and 'location' in self.me:
                try:
                    city, country = GoogleGeocoder().getCityCountry(self.me['location']['name'])
                except (KeyError, IndexError):
                    pass
                else:
                    initial['addresses__country'] = country
                    initial['addresses__city'] = city
            
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial)
        return super(ProductWizard, self).get_form(step, data, files)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/product_register.html'
        elif issubclass(self.form_list[step], ProductForm):
            return 'products/product_create.html'
        else:
            return 'products/product_missing.html'
            
class MessageWizard(GenericFormWizard):
    
    required_fields = ['username', 'password1', 'password2']
    
    def __call__(self, request, product_id, recipient_id, *args, **kwargs):
        product = get_object_or_404(Product, pk=product_id)
        recipient = get_object_or_404(Patron, pk=recipient_id)
        self.extra_context.update({'product': product})
        self.extra_context.update({'recipient': recipient})
        if request.user.is_authenticated():
            return super(MessageWizard, self).__call__(request, *args, **kwargs)
        if EmailAuthenticationForm not in self.form_list:
            self.form_list.append(EmailAuthenticationForm)
        if EmailAuthenticationForm in self.form_list:
            if not next((form for form in self.form_list if getattr(form, '__name__', None) == 'MissingInformationForm'), None):
                form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                form.is_valid()
                missing_fields, missing_form = make_missing_data_form(form.get_user(), self.required_fields)
                if missing_fields:
                    self.form_list.append(missing_form)
        return super(MessageWizard, self).__call__(request, *args, **kwargs)
        
    def done(self, request, form_list):
        #TODO Repeat codes, needs some refactoring
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                fb_session = auth_form.fb_session
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
                    #Assign affiliate tag, no need to save, since missing_form should do it for us
                    new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user
        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone, avatar = missing_form.save()
        # Create message
        product = self.extra_context["product"]
        recipient = self.extra_context["recipient"]
        if new_patron == product.owner:
            messages.error(request, _(u"Vous ne pouvez pas vous envoyer des messages."))
            return redirect_to(request, product.get_absolute_url())
        message_form = form_list[0]
        message_form.save(product=product, sender=new_patron, recipient=recipient)
        messages.success(request, _(u"Votre message a bien été envoyé au propriétaire"))
        return redirect_to(request, product.get_absolute_url())
    
    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if next_form.__name__ == 'MissingInformationForm':
            initial = {
                'username': self.me.get('username', '') if self.me else '',
            }
            
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial)
        return super(MessageWizard, self).get_form(step, data, files)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'django_messages/message_register.html'
        elif issubclass(self.form_list[step], MessageEditForm):
            return 'django_messages/message_create.html'
        else:
            return 'django_messages/message_missing.html'
    
class AlertWizard(GenericFormWizard):
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)

        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
                if hasattr(settings, 'AFFILIATE_TAG'):
                    # Assign affiliate tag, no need to save, since missing_form should do it for us
                    new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user

        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone = missing_form.save()
        # Create and send alerts
        alert_form = form_list[0]
        alert_form.instance.patron = new_patron
        alert_form.instance.address = new_address
        alert = alert_form.save()

        if not settings.AUTHENTICATION_BACKENDS[0] == 'eloue.accounts.auth.PrivatePatronModelBackend':
            alert.send_alerts()

        messages.success(request, _(u"Votre alerte a bien été créée"))
        return redirect_to(request, reverse("alert_edit"), permanent=False)

    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/alert_register.html'
        elif issubclass(self.form_list[step], AlertForm):
            return 'products/alert_create.html'
        else:
            return 'products/alert_missing.html'
    
class AlertAnswerWizard(GenericFormWizard):
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
                if hasattr(settings, 'AFFILIATE_TAG'):
                    # Assign affiliate tag, no need to save, since missing_form should do it for us
                    new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user

        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone = missing_form.save()

        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_address
        product = product_form.save()

        for unit in UNIT.keys():
            field = "%s_price" % unit.lower()
            if field in product_form.cleaned_data and product_form.cleaned_data[field]:
                product.prices.create(
                    unit=UNIT[unit],
                    amount=product_form.cleaned_data[field]
                )

        if product_form.cleaned_data.get('picture_id', None):
            product.pictures.add(Picture.objects.get(pk=product_form.cleaned_data['picture_id']))

        GoalRecord.record('new_object', WebUser(request))

        alert = self.extra_context['alert']
        alert.send_alerts_answer(product)
        
        return redirect_to(request, reverse("alert_inform_success", args=[alert.pk]), permanent=False)

    def get_form(self, step, data=None, files=None):
        if issubclass(self.form_list[step], ProductForm):
            if files and '0-picture' in files:  # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=Product(quantity=1, deposit_amount=0))
        if not issubclass(self.form_list[step], (ProductForm, EmailAuthenticationForm)):
            initial = {
                'addresses__country': settings.LANGUAGE_CODE.split('-')[1].upper(),
            }
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=initial)
        return super(ProductWizard, self).get_form(step, data, files)

    def parse_params(self, request, *args, **kwargs):
        alert = get_object_or_404(Alert, pk=kwargs["alert_id"])
        self.extra_context['alert'] = alert

    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/product_register.html'
        elif issubclass(self.form_list[step], ProductForm):
            return 'products/product_create.html'
        else:
            return 'products/product_missing.html'
            
        
