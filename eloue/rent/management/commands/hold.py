# -*- coding: utf-8 -*-
import logbook

from datetime import datetime, timedelta

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand

log = logbook.Logger('eloue.rent.hold')


class Command(BaseCommand):
    help = "Hold payments on a hourly basis"
    
    def handle(self, *args, **options):
        from eloue.rent.models import Booking
        log.info('Starting hourly payment holder process')
        domain = Site.objects.get_current().domain
        dtime = datetime.now() + timedelta(hours=1)
        for booking in Booking.objects.pending().filter(started_at__contains=' %02d' % dtime.hour, started_at__day=dtime.day, started_at__month=dtime.month, started_at__year=dtime.year):
            booking.hold(
                # FIXME : This should be https but these are dummy urls after all
                cancel_url="http://%s%s" % (domain, reverse("booking_failure", args=[booking.pk.hex])),
                return_url="http://%s%s" % (domain, reverse("booking_success", args=[booking.pk.hex])),
            )
            booking.booking_state = Booking.BOOKING_STATE.ONGOING
            booking.save()
        log.info('Finished hourly payment holder process')
    
