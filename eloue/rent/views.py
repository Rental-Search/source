# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from eloue.rent.models import Booking

log = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def ipn_handler(request):
    # FIXME : dumb ipn handler
    log.info(request.POST)
    return HttpResponse('OKAY')
