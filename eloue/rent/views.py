# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from eloue.rent.decorators import validate_ipn
from eloue.rent.forms import PreApprovalIPNForm, PayIPNForm
from eloue.rent.models import Booking

log = logging.getLogger(__name__)

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
