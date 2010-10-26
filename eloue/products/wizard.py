# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.contrib.formtools.wizard import FormWizard
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, PATRON_FIELDS, ADDRESS_FIELDS, make_missing_data_form
from eloue.accounts.models import Patron, Address
from eloue.products.forms import ProductForm
from eloue.products.models import Product


class ProductWizard(FormWizard):
    def done(self, request, form_list):
        missing_form = filter(lambda el: el.__name__ == 'MissingInformationForm', form_list)
        if missing_form: # Fill missing information
            missing_form = missing_form[0]
        
        auth_form = filter(lambda el: isinstance(el, EmailAuthenticationForm), form_list)
        if auth_form: # Create new Patron
            auth_form = auth_form[0]
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
        
        # Assign missing data to Patron
        for field in PATRON_FIELDS:
            if field in missing_form.cleaned_data:
                setattr(new_patron, field, missing_form.cleaned_data[field])
        new_patron.save()
        
        # Assign missing data to Address
        if 'address' in missing_form.cleaned_data:
            new_address = missing_form.cleaned_data['address']
        else:
            new_address = Address(patron=new_patron), False
            for field in ADDRESS_FIELDS:
                if field in missing_form.cleaned_data:
                    setattr(new_address, field, missing_form.cleaned_data[field])
            new_address.save()
        
        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_address
        product = product_form.save()
        
        GoalRecord.record('new_object', WebUser(request))
        return redirect_to(request, product.get_absolute_url())
    
    def get_form(self, step, data=None):
        if issubclass(self.form_list[step], ProductForm):
            return self.form_list[step](data, prefix=self.prefix_for_step(step), 
                initial=self.initial.get(step, None), instance=Product())
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return self.form_list[step](None, data, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None))
        return super(ProductWizard, self).get_form(step, data)
    
    def process_step(self, request, form, step):
        if step == 0: # Check if we need the user to be authenticated
            if request.user.is_anonymous() and EmailAuthenticationForm not in self.form_list:
                self.form_list.append(EmailAuthenticationForm)
        if step == 1: # Check if we have necessary information from this user
            missing_fields, form_class = make_missing_data_form(form.get_user())
            if missing_fields and not any(map(lambda el: el.__name__ == 'MissingInformationForm', self.form_list)):
                self.form_list.append(form_class)
        return super(ProductWizard, self).process_step(request, form, step)
    
    def get_template(self, step):
        stage = {0: 'create', 1: 'register', 2:'missing'}.get(step)
        return 'products/product_%s.html' % stage
    
