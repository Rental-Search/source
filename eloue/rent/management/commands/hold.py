# -*- coding: utf-8 -*-
import logbook

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

log = logbook.Logger('eloue.rent.hold')


class Command(BaseCommand):
    help = "Hold payments on a hourly basis"
    
    def handle(self, *args, **options):
        
        from eloue.rent.models import Booking
        log.info('Starting hourly payment holder process')
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        dtime = datetime.now() + timedelta(hours=1)
        for booking in Booking.objects.pending().filter(started_at__contains=' %02d' % dtime.hour, started_at__day=dtime.day, started_at__month=dtime.month, started_at__year=dtime.year):
            booking.hold(
                cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
                return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
            )
            booking.booking_state = Booking.BOOKING_STATE.ONGOING
            booking.save()
        log.info('Finished hourly payment holder process')
    
