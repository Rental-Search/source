# -*- coding: utf-8 -*-
import urllib

from django.conf import settings
from django.contrib.auth import login
from django.views.generic.simple import direct_to_template, redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.products.models import Product
from eloue.rent.models import Booking, PAYMENT_STATE
from eloue.rent.forms import BookingForm
from eloue.wizard import GenericFormWizard


class BookingWizard(GenericFormWizard):    
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        
        if request.user.is_anonymous(): # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
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
        
        booking_form = form_list[0]
        booking_form.instance.total_amount = Booking.calculate_price(booking_form.instance.product,
            booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])
        booking_form.instance.borrower = new_patron
        booking = booking_form.save()
        
        booking.preapproval(
            cancel_url="http://cancel.me",
            return_url="http://return.me",
            ip_address=request.META['REMOTE_ADDR']
        )
        
        if booking.payment_state == PAYMENT_STATE.AUTHORIZED:
            GoalRecord.record('rent_object_pre_paypal', WebUser(request))
            return redirect_to(request, settings.PAYPAL_COMMAND % urllib.urlencode({ 'cmd':'_ap-preapproval', 'preapprovalkey':booking.preapproval_key }))
        return direct_to_template(request, template="rent/booking_preapproval.html", extra_context={
            'booking':booking,
        })
    
    def get_form(self, step, data=None, files=None):
        if issubclass(self.form_list[step], BookingForm):
            product = self.extra_context['product']
            booking = Booking(product=product, owner=product.owner)
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=booking)
        return super(BookingWizard, self).get_form(step, data, files)
    
    def parse_params(self, request, *args, **kwargs):
        self.extra_context['product'] = Product.objects.get(pk=kwargs['product_id'])
    
    def process_step(self, request, form, step):
        return super(BookingWizard, self).process_step(request, form, step)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'rent/booking_register.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'rent/booking_basket.html'
        else:
            return 'rent/booking_missing.html'
    
