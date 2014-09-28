# -*- coding: utf-8 -*-
import logbook
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand

from payments.paybox_payment import PayboxException

from eloue.decorators import activate_language

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

class DjangoMailHandler(logbook.MailHandler):

    def deliver(self, msg, recipients):
        """Delivers the given message to a list of recpients."""
        mail.send_mail("Payment error", msg.as_string(), self.from_addr, recipients)

handler = DjangoMailHandler(settings.SERVER_EMAIL, ['ops@e-loue.com'],
                              format_string=logbook.handlers.MAIL_FORMAT_STRING, level='INFO', bubble = True, record_delta=timedelta(seconds=0))


log = logbook.Logger('eloue.rent.ongoing')


class Command(BaseCommand):
    help = "Batch wire transfer payment 24 hours after the start of the rent"
    
    @activate_language
    def handle(self, *args, **options):
        """Find ongoing rent, hold money and the ipn callback do the rest by moving them in ONGOING state"""
        from rent.models import Booking
        raise NotImplementedError('not ready yet')
        log.info('Starting hourly ongoing mover process')

        now = datetime.now()
        stime = now - timedelta(days=2)
        etime = now - timedelta(days=1)

        for booking in Booking.objects.ongoing().filter(started_at__gte=stime, started_at__lt=etime):
            with handler:
                print booking.owner.rib, booking.net_price
        log.info('Finished hourly ongoing mover process')
    
