# -*- coding: utf-8 -*-
import logbook

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.rent.decorators import validate_ipn
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
            booking.payment_state = Booking.PAYMENT_STATE.AUTHORIZED
            booking.borrower.paypal_email = form.cleaned_data['sender_email']
            booking.borrower.save()
        else:
            booking.payment_state = Booking.PAYMENT_STATE.REJECTED
        booking.save()
    return HttpResponse()


@require_POST
@csrf_exempt
@validate_ipn
def pay_ipn(request):
    form = PayIPNForm(request.POST)
    if form.is_valid():
        pass # TODO : deal with data
    return HttpResponse()

   
@never_cache
def booking_create(request, *args, **kwargs):
    wizard = BookingWizard([BookingForm,EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return direct_to_template(request, template="rent/booking_success.html", context={
        'booking':booking
    })


def booking_failure(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return direct_to_template(request, template="rent/booking_failure.html", context={
        'booking':booking
    })
