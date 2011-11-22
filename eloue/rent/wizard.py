# -*- coding: utf-8 -*-
import datetime
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template, redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron, Avatar
from eloue.geocoder import GoogleGeocoder
from eloue.products.forms import FacetedSearchForm
from eloue.products.models import Product, PAYMENT_TYPE
from eloue.rent.models import Booking
from eloue.rent.forms import BookingForm, BookingConfirmationForm
from eloue.wizard import GenericFormWizard

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


class BookingWizard(GenericFormWizard):
    
    required_fields = [
        'username', 'password1', 'password2', 'is_professional', 'company_name', 'first_name', 'last_name',
        'phones', 'phones__phone', 'addresses',
        'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country'
    ]

    def done(self, request, form_list):
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
        
        booking_form = form_list[0]
        
        if new_patron == booking_form.instance.product.owner:
            messages.error(request, _(u"Vous ne pouvez pas louer vos propres objets"))
            return redirect_to(request, booking_form.instance.product.get_absolute_url())
        
        booking_form.instance.ip = request.META.get('REMOTE_ADDR', None)
        booking_form.instance.total_amount = Booking.calculate_price(booking_form.instance.product,
            booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])[1]
        booking_form.instance.borrower = new_patron
        payment_type = booking_form.instance.product.payment_type
        booking = booking_form.save()
        booking.init_payment_processor()
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        
        booking.preapproval(
            cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
            return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
            ip_address=request.META['REMOTE_ADDR']
        )
        
        if booking.state != Booking.STATE.REJECTED:
            GoalRecord.record('rent_object_pre_paypal', WebUser(request))
            if payment_type == PAYMENT_TYPE.NOPAY:
                from django.views.generic.list_detail import object_detail
                return object_detail(request, queryset=Booking.on_site.all(), object_id=booking.pk.hex, #test
                     template_name='rent/booking_success.html', template_object_name='booking')
            return redirect_to(request, settings.PAYPAL_COMMAND % urllib.urlencode({'cmd': '_ap-preapproval',
                'preapprovalkey': booking.preapproval_key}))
        return direct_to_template(request, template="rent/booking_preapproval.html", extra_context={
            'booking': booking,
        })
    
    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if issubclass(next_form, BookingForm):
            product = self.extra_context['product']
            booking = Booking(product=product, owner=product.owner)
            started_at = datetime.datetime.now() + datetime.timedelta(days=1)
            ended_at = started_at + datetime.timedelta(days=1)
            initial = {
                'started_at': [started_at.strftime('%d/%m/%Y'), started_at.strftime("08:00:00")],
                'ended_at': [ended_at.strftime('%d/%m/%Y'), ended_at.strftime("08:00:00")],
                # is 'total_amount' really necessary?
                'total_amount': Booking.calculate_price(product, started_at, ended_at)[1]
            }
            initial.update(self.initial.get(step, {}))
            return next_form(data, files, prefix=self.prefix_for_step(step),
                initial=initial, instance=booking)
        elif next_form.__name__ == 'MissingInformationForm':
        #if not issubclass(self.form_list[step], (BookingForm, EmailAuthenticationForm, BookingConfirmationForm)):
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
            
        return super(BookingWizard, self).get_form(step, data, files)
    
    def process_step(self, request, form, step):
        super(BookingWizard, self).process_step(request, form, step)
        form = self.get_form(0, request.POST, request.FILES)
        if form.is_valid():
            self.extra_context['preview'] = form.cleaned_data
    
    def parse_params(self, request, *args, **kwargs):
        product = get_object_or_404(Product.on_site.active(), pk=kwargs['product_id'])
        self.extra_context['product'] = product
        self.extra_context['search_form'] = FacetedSearchForm()
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'rent/booking_register.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'products/product_detail.html'
        elif issubclass(self.form_list[step], BookingConfirmationForm):
            return 'rent/booking_confirm.html'
        else:
            return 'rent/booking_missing.html'
    
