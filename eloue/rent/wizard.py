# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.contrib.formtools.wizard import FormWizard
from django.views.generic.simple import direct_to_template

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron
from eloue.products.models import Product
from eloue.rent.models import Booking
from eloue.rent.forms import BookingForm


class BookingWizard(FormWizard):    
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
        
        booking_form = form_list[0]
        booking_form.instance.borrower = new_patron
        booking = booking_form.save()
        
        booking.preapproval(
            cancel_url=None,
            return_url=None,
            ip_address=request.META['REMOTE_ADDR']
        )
        
        GoalRecord.record('rent_object', WebUser(request))
        return direct_to_template(request, template="rent/booking_preapproval.html", extra_context={
            'booking':booking,
        })
    
    def get_form(self, step, data=None):
        if issubclass(self.form_list[step], BookingForm):
            product = self.extra_context['product']
            booking = Booking(product=product, owner=product.owner)
            return self.form_list[step](data, prefix=self.prefix_for_step(step), 
                initial=self.initial.get(step, None), instance=booking)
        return super(BookingWizard, self).get_form(step, data)
    
    def parse_params(self, request, *args, **kwargs):
        self.extra_context['product'] = Product.objects.get(pk=kwargs['product_id'])
    
    def process_step(self, request, form, step):
        if step == 0: # Check if we need the user to be authenticated
            if request.user.is_anonymous() and EmailAuthenticationForm not in self.form_list:
                self.form_list.append(EmailAuthenticationForm)
        if step == 1: # Check if we have necessary information from this user
            missing_fields, form_class = make_missing_data_form(form.get_user())
            if missing_fields and not any(map(lambda el: el.__name__ == 'MissingInformationForm', self.form_list)):
                self.form_list.append(form_class)
        return super(BookingWizard, self).process_step(request, form, step)
    
    def get_template(self, step):
        stage = {0: 'basket', 1: 'register', 2:'missing'}.get(step)
        return 'rent/booking_%s.html' % stage
    
