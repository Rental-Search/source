# -*- coding: utf-8 -*-
import logbook

from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

log = logbook.Logger('eloue.rent.outdated')


class Command(BaseCommand):
    help = "Find outdated rentals and move them in OUTDATED state."
    
    def handle(self, *args, **options):
        """Find outdated rentals and move them in OUTDATED state."""
        from eloue.rent.models import Booking
        log.info('Starting hourly outdater mover process')
        Booking.objects.filter(
            state__in=[Booking.STATE.AUTHORIZING, Booking.STATE.AUTHORIZED],
            started_at__gte=datetime.now()
        ).update(state=Booking.STATE.OUTDATED)
        log.info('Finished hourly outdater mover process')
    
