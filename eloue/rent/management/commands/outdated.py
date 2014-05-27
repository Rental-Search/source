# -*- coding: utf-8 -*-
import logbook

from datetime import datetime

from django.core.management.base import BaseCommand

from eloue.decorators import activate_language

log = logbook.Logger('eloue.rent.outdated')


class Command(BaseCommand):
    help = "Find outdated rentals and move them in OUTDATED state."
    
    @activate_language
    def handle(self, *args, **options):
        """Find outdated rentals and move them in OUTDATED state."""
        from rent.models import Booking
        log.info('Starting hourly outdater mover process')
        Booking.objects.filter(
            state__in=[Booking.STATE.AUTHORIZING, Booking.STATE.AUTHORIZED],
            started_at__lt=datetime.now()
        ).update(state=Booking.STATE.OUTDATED)
        log.info('Finished hourly outdater mover process')
    
