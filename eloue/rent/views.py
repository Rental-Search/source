# -*- coding: utf-8 -*-
import logbook

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.rent.decorators import validate_ipn
from eloue.rent.forms import BookingForm, PreApprovalIPNForm, PayIPNForm
from eloue.rent.wizard import BookingWizard

log = logbook.Logger('eloue.rent')


@require_POST
@csrf_exempt
@validate_ipn
def preapproval_ipn(request):
    form = PreApprovalIPNForm(request.POST)
    if form.is_valid():
        pass # TODO : deal with data
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
