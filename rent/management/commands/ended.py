# -*- coding: utf-8 -*-
import logbook

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from eloue.decorators import activate_language

log = logbook.Logger('eloue.rent.ended')


class Command(BaseCommand):
    help = "Find ended rentals and move them to ENDED state"
    
    @activate_language
    def handle(self, *args, **options):
        """Find ending rent and move them as ENDED."""
        from rent.models import Booking
        log.info('Starting hourly ender mover process')
        dtime = datetime.now() + timedelta(hours=1)
        for booking in Booking.objects.ongoing().filter(
            ended_at__contains=' %02d' % dtime.hour,
            ended_at__day=dtime.day, ended_at__month=dtime.month,
            ended_at__year=dtime.year):
                booking.end()
                booking.save()
        log.info('Finished hourly ender mover process')
    
