# -*- coding: utf-8 -*-
import logbook

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from eloue.decorators import activate_language

log = logbook.Logger('eloue.rent.recovery')


class Command(BaseCommand):
    help = "Try to recover client who haven't finished their booking"
    
    @activate_language
    def handle(self, *args, **options):
        from eloue.rent.models import Booking
        dtime = datetime.now() + timedelta(hours=1)
        for booking in Booking.objects.authorizing().filter(ended_at__contains=' %02d' % dtime.hour,
            ended_at__day=dtime.day, ended_at__month=dtime.month,
            ended_at__year=dtime.year):
            booking.send_recovery_email()
    
