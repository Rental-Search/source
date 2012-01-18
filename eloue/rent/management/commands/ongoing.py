# -*- coding: utf-8 -*-
import logbook

from datetime import datetime, timedelta
from paypalx import PaypalError
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand

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
    help = "Start a renting by holding money on a hourly basis"
    
    @activate_language
    def handle(self, *args, **options):
        """Find ongoing rent, hold money and the ipn callback do the rest by moving them in ONGOING state"""
        from eloue.rent.models import Booking
        log.info('Starting hourly ongoing mover process')
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        dtime = datetime.now() + timedelta(hours=1)
        for booking in Booking.objects.pending().filter(started_at__contains=' %02d' % dtime.hour, started_at__day=dtime.day, started_at__month=dtime.month, started_at__year=dtime.year):
            booking.init_payment_processor()
            with handler:
                try:
                    booking.hold(
                        cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
                        return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
                    )
                except PaypalError as e:
                    log.exception("For booking {pk}, exception occured: {e}".format(e=e, pk=booking.pk))
                    continue
            if booking.not_need_ipn():
                booking.state = Booking.STATE.ONGOING
                booking.save()
        log.info('Finished hourly ongoing mover process')
    
