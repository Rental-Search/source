# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.products.forms import ProductForm
from eloue.products.models import Product, Picture, UNIT
from eloue.wizard import CustomFormWizard

class ProductWizard(CustomFormWizard):
    def done(self, request, form_list):
        missing_form = form_list[-1]
        
        if request.user.is_anonymous(): # Create new Patron
            auth_form = form_list[1]
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'], 
                    auth_form.cleaned_data['email'], auth_form.cleaned_data['password'])
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user
        
        missing_form.instance = new_patron
        new_patron, new_address, new_phone = missing_form.save()
        
        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_address
        product = product_form.save()
        product.prices.create(unit=UNIT.DAY, amount=product_form.cleaned_data['price'])
        
        if product_form.cleaned_data.get('picture_id', None):
            product.pictures.add(Picture.objects.get(pk=product_form.cleaned_data['picture_id']))
        
        GoalRecord.record('new_object', WebUser(request))
        return redirect_to(request, product.get_absolute_url())
    
    def get_form(self, step, data=None, files=None):
        if issubclass(self.form_list[step], ProductForm):
            if files and '0-picture' in files: # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step), 
                initial=self.initial.get(step, None), instance=Product(quantity=1))
        return super(ProductWizard, self).get_form(step, data, files)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/product_register.html'
        elif issubclass(self.form_list[step], ProductForm):
            return 'products/product_create.html'
        else:
            return 'products/product_missing.html'
    
