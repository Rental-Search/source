# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm
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
    

    def __call__(self, request, product_id, recipient_id, *args, **kwargs):
        product = get_object_or_404(Product, pk=product_id)
        recipient = get_object_or_404(Patron, pk=recipient_id)
        self.extra_context.update({'product': product})
        self.extra_context.update({'recipient': recipient})
        return super(MessageWizard, self).__call__(request, *args, **kwargs)
        
    def done(self, request, form_list):
        #TODO Repeat codes, needs some refactoring 
        """
        product = get_object_or_404(Product, pk=product_id)
        sender = request.user
        messages_form = MessageEditForm(data=request.POST)
        if messages_form.is_valid():
            messages_form.save(product=product, sender=request.user)
            messages.success(request, _(u"Une question du produit a été envoyé !"))
        return direct_to_template(request, 'products/product_detail.html', extra_context={'product': product, 'messages_form':messages_form})    
        """
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
        
        # Create message
        product = self.extra_context["product"]
        recipient = self.extra_context["recipient"]
        message_form = form_list[0]
        print ">>>>>>>>> message form data >>>>>>>>", request.POST
        message_form.save(product=product, sender=new_patron, recipient=recipient)
        messages.success(request, _(u"Une question du produit a été envoyé !"))

        GoalRecord.record('new_object', WebUser(request))
        
        return direct_to_template(request, 'products/product_detail.html', extra_context={'product': product, 'messages_form':message_form})   
        
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/product_register.html'
        elif issubclass(self.form_list[step], MessageEditForm):
            print '>>>>>>> messages form called  >>>>>>'
            return 'products/message_edit.html'
        else:
            return 'products/product_missing.html'




