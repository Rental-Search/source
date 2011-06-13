# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron
from eloue.products.forms import ProductForm, MessageEditForm
from eloue.products.models import Product, Picture, UNIT
from eloue.wizard import GenericFormWizard
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template, redirect_to


class ProductWizard(GenericFormWizard):
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
        return redirect_to(request, product.get_absolute_url(), permanent=False)
    
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
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
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
            new_patron, new_address, new_phone = missing_form.save()
        # Create message
        product = self.extra_context["product"]
        recipient = self.extra_context["recipient"]
        message_form = form_list[0]
        message_form.save(product=product, sender=new_patron, recipient=recipient)
        messages.success(request, _(u"Une question du produit a été envoyé !"))
        GoalRecord.record('new_object', WebUser(request))
        return redirect_to(request, product.get_absolute_url())
        
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'django_messages/message_register.html'
        elif issubclass(self.form_list[step], MessageEditForm):
            return 'products/message_edit.html'
        else:
            return 'django_messages/message_missing.html'



