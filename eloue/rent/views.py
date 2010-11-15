# -*- coding: utf-8 -*-
import logbook

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template, redirect_to

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.products.models import Product
from eloue.rent.decorators import validate_ipn, ownership_required
from eloue.rent.forms import BookingForm, PreApprovalIPNForm, PayIPNForm
from eloue.rent.models import Booking
from eloue.rent.wizard import BookingWizard

log = logbook.Logger('eloue.rent')


@require_POST
@csrf_exempt
@validate_ipn
def preapproval_ipn(request):
    form = PreApprovalIPNForm(request.POST)
    if form.is_valid():
        booking = Booking.objects.get(preapproval_key=form.cleaned_data['preapproval_key'])
        if form.cleaned_data['approved'] and form.cleaned_data['status'] == 'ACTIVE':
            # Changing state
            booking.payment_state = Booking.PAYMENT_STATE.AUTHORIZED
            booking.booking_state = Booking.BOOKING_STATE.ASKED
            booking.borrower.paypal_email = form.cleaned_data['sender_email']
            booking.borrower.save()
            # Sending email
            booking.send_ask_email()
        else:
            booking.payment_state = Booking.PAYMENT_STATE.REJECTED
            booking.booking_state = Booking.BOOKING_STATE.REJECTED
        booking.save()
    return HttpResponse()


@require_POST
@csrf_exempt
@validate_ipn
def pay_ipn(request):
    form = PayIPNForm(request.POST)
    if form.is_valid():
        booking = Booking.objects.get(pay_key=form.cleaned_data['pay_key'])
        if form.cleaned_data['action_type'] == 'PAY_PRIMARY' and form.cleaned_data['status'] == 'INCOMPLETE':
            booking.payment_state = Booking.PAYMENT_STATE.HOLDED
        booking.save()
    return HttpResponse()

   
@never_cache
def booking_create(request, *args, **kwargs):
    product = get_object_or_404(Product, pk=kwargs['product_id'])
    if product.slug != kwargs['slug']:
        return redirect_to(request, product.get_absolute_url())
    wizard = BookingWizard([BookingForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


def booking_success(request, booking_id):
    return object_detail(request, queryset=Booking.objects.all(), object_id=booking_id, template_name='rent/booking_success.html', template_object_name='booking')


def booking_failure(request, booking_id):
    return object_detail(request, queryset=Booking.objects.all(), object_id=booking_id, template_name='rent/booking_failure.html',  template_object_name='booking')


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_detail(request, booking_id):
    return object_detail(request, queryset=Booking.objects.all(), object_id=booking_id, template_name='rent/booking_detail.html', template_object_name='booking')


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_accept(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST:
        booking.booking_state = Booking.BOOKING_STATE.PENDING
        booking.send_acceptation_email()
        booking.save()
    return direct_to_template(request, 'rent/booking_accept.html', extra_context={ 'booking':booking })


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_reject(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST:
        booking.booking_state = Booking.BOOKING_STATE.REJECTED
        booking.send_rejection_email()
        booking.save()
    return direct_to_template(request, 'rent/booking_reject.html', extra_context={ 'booking':booking })


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_close(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST:
        booking.pay()
        booking.booking_state = Booking.BOOKING_STATE.CLOSED
        booking.save()
    return direct_to_template(request, 'rent/booking_close.html', extra_context={ 'booking':booking })


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_incident(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST: # TODO : Do we need more ?!
        booking.booking = Booking.BOOKING_STATE.INCIDENT
        booking.save()
    return direct_to_template(request, 'rent/booking_incident.html', extra_context={ 'booking':booking })

