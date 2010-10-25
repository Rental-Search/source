# -*- coding: utf-8 -*-
import django.forms as forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.formtools.wizard import FormWizard
from django.utils.datastructures import SortedDict
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron, Address
from eloue.products.forms import ProductForm
from eloue.products.models import Product

PATRON_FIELDS = ['first_name', 'last_name', 'username']

def fields_for_instance(instance, fields=None, exclude=None, widgets=None):
    field_list = []
    opts = instance._meta
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if hasattr(instance, f.name) and getattr(instance, f.name):
            continue
        if widgets and f.name in widgets:
            kwargs = {'widget': widgets[f.name]}
        else:
            kwargs = {}
        formfield = f.formfield(**kwargs)
        if formfield:
            field_list.append((f.name, formfield))
    return SortedDict(field_list)

def make_missing_data_form(instance):
    fields = {}
    if instance:
        fields.update(fields_for_instance(instance, fields=PATRON_FIELDS))
        if not instance.addresses.exists():
            fields.update(fields_for_instance(Address, exclude=['patron']))
        else:
            fields.update({ 'address':forms.ModelChoiceField(queryset=instance.addresses.all()) })
    else:
        fields.update(fields_for_instance(Patron, fields=PATRON_FIELDS))
        fields.update(fields_for_instance(Address, exclude=['patron']))
    form_class = type('MissingForm', (forms.BaseForm,), { 'base_fields': fields })
    return fields != {}, form_class

class ProductWizard(FormWizard):
    def done(self, request, form_list):
        if len(form_list) > 2: # Fill missing information
            missing_form = form_list[2] 
        
        if len(form_list) > 1 and isinstance(form_list[1], EmailAuthenticationForm): # Authenticate user
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
        
        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_patron.addresses.all()[0]
        product = product_form.save()
        
        GoalRecord.record('new_object', WebUser(request))
        return redirect_to(request, product.get_absolute_url())
    
    def get_form(self, step, data=None):
        if isinstance(self.form_list[step], ProductForm):
            return self.form_list[step](data, prefix=self.prefix_for_step(step), 
                initial=self.initial.get(step, None), instance=Product())
        if isinstance(self.form_list[step], EmailAuthenticationForm):
            return self.form_list[step](None, data, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None))
        return super(ProductWizard, self).get_form(step, data)
    
    def process_step(self, request, form, step):
        if step == 0: # Check if we need the user to be authenticated
            if request.user.is_anonymous() and EmailAuthenticationForm not in self.form_list:
                self.form_list.append(EmailAuthenticationForm)
        if step == 1: # Check if we have necessary information from this user
            instance = form.get_user()
            missing_fields, form_class = make_missing_data_form(instance)
            if missing_fields and not any(map(lambda el: el.__name__ == 'MissingForm', self.form_list)):
                self.form_list.append(form_class)
        return super(ProductWizard, self).process_step(request, form, step)
    
    def get_template(self, step):
        stage = {0: 'create', 1: 'register', 2:'missing'}.get(step)
        return 'products/product_%s.html' % stage
    
