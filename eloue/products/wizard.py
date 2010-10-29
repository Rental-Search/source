# -*- coding: utf-8 -*-
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.products.forms import ProductForm
from eloue.products.models import Product, Picture, UNIT
from eloue.wizard import GenericFormWizard

class ProductWizard(GenericFormWizard):
    def done(self, request, form_list):
        new_patron, new_address, new_phone = super(ProductWizard, self).done(request, form_list)    
        
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
    
    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated(): # When user is authenticated
            if EmailAuthenticationForm in self.form_list:
                self.form_list.remove(EmailAuthenticationForm)
            if not any(map(lambda el: getattr(el, '__name__', None) == 'MissingInformationForm', self.form_list)):
                self.form_list.append(make_missing_data_form(request.user))
        else: # When user is anonymous
            if EmailAuthenticationForm not in self.form_list:
                self.form_list.append(EmailAuthenticationForm)
            if EmailAuthenticationForm in self.form_list:
                if not any(map(lambda el: getattr(el, '__name__', None) == 'MissingInformationForm', self.form_list)):
                    form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                    form.is_valid() # Here to fill form user_cache
                    self.form_list.append(make_missing_data_form(form.get_user()))
        return super(ProductWizard, self).__call__(request, *args, **kwargs)
    
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
    
