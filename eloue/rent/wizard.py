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
from eloue.rent.models import Booking, BorrowerComment
from eloue.rent.forms import BookingForm, BookingConfirmationForm
from eloue.wizard import NewGenericFormWizard

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


class BookingWizard(NewGenericFormWizard):
    
    def __init__(self, *args, **kwargs):
        super(BookingWizard, self).__init__(*args, **kwargs)
        self.required_fields = [
          'username', 'password1', 'password2', 'is_professional', 'company_name', 'first_name', 'last_name', 'avatar',
          'phones', 'phones__phone', 'addresses',
          'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country'
        ]

    def __call__(self, request, *args, **kwargs):
        product = get_object_or_404(Product.on_site.select_related(), pk=kwargs['product_id'])
        from eloue.products.search_indexes import product_search
        self.extra_context={
            'product_list': product_search.more_like_this(product)[:4]
        }
        return super(BookingWizard, self).__call__(request, *args, **kwargs)

    def done(self, request, form_list):
        super(BookingWizard, self).done(request, form_list)
        booking_form = form_list[0]
        
        if self.new_patron == booking_form.instance.product.owner:
            messages.error(request, _(u"Vous ne pouvez pas louer vos propres objets"))
            return redirect_to(request, booking_form.instance.product.get_absolute_url())
        
        booking_form.instance.ip = request.META.get('REMOTE_ADDR', None)
        booking_form.instance.total_amount = Booking.calculate_price(booking_form.instance.product,
            booking_form.cleaned_data['started_at'], booking_form.cleaned_data['ended_at'])[1]
        booking_form.instance.borrower = self.new_patron
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
        return super(BookingWizard, self).get_form(step, data, files)
    
    def process_step(self, request, form, step):
        super(BookingWizard, self).process_step(request, form, step)
        form = self.get_form(0, request.POST, request.FILES)
        if form.is_valid():
            self.extra_context['preview'] = form.cleaned_data
    
    def parse_params(self, request, *args, **kwargs):
        product = get_object_or_404(Product.on_site.active().select_related(), pk=kwargs['product_id'])
        try:
            self.extra_context['product'] = product.realestateproduct
        except Product.DoesNotExist:
            try:
                self.extra_context['product'] = product.carproduct
            except Product.DoesNotExist:
                self.extra_context['product'] = product
        self.extra_context['search_form'] = FacetedSearchForm()
        self.extra_context['comments'] = BorrowerComment.objects.filter(booking__product=product)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], BookingForm):
            return 'products/product_detail.html'
        elif issubclass(self.form_list[step], BookingConfirmationForm):
            return 'rent/booking_confirm.html'
        else:
            return 'accounts/auth_missing.html'
    
