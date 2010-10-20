# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.contrib.formtools.wizard import FormWizard
from django.views.generic.simple import redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.models import Patron

class ProductWizard(FormWizard):
    def done(self, request, form_list):
        # Authenticate user
        auth_form = form_list[1]
        if not request.user.is_authenticated():
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(auth_form.cleaned_data['email'], auth_form.cleaned_data['password'])
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user
        
        # Fill missing information
        # missing_form = form_list[2]
        # missing_form.save()
        
        # Create product
        product_form = form_list[0]
        product_form.owner = new_patron
        product = product_form.save()
        
        GoalRecord.record('new_object', WebUser(request))
        return redirect_to(request, product.get_absolute_url())
    
    def process_step(self, request, form, step):
        
        return super(ProductWizard, self).process_step(request, form, step)
    
    def get_template(self, step):
        stage = {0: 'create', 1: 'register', 2:'missing'}.get(step)
        return 'products/product_%s.html' % stage
    
    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(ProductWizard, self).__call__(request, *args, **kwargs)
    
