# -*- coding: utf-8 -*-
import datetime
import inspect

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import mail

import logbook


class DjangoMailHandler(logbook.MailHandler):

    def deliver(self, msg, recipients):
        """Delivers the given message to a list of recpients."""
        mail.send_mail("importation error", msg.as_string(), self.from_addr, recipients)

handler = DjangoMailHandler(settings.SERVER_EMAIL, ['ops@e-loue.com'],
                              format_string=logbook.handlers.MAIL_FORMAT_STRING, level='INFO', bubble = True, record_delta=datetime.timedelta(seconds=0))

log = logbook.Logger('eloue.rent.sources')

class Command(BaseCommand):
    help = "Update sources for affiliation."
    args = "[source_prefix source_prefix ...]"

    def handle(self, *args, **options):
        from eloue.products.search_indexes import product_search
        now = datetime.datetime.now()
        products = product_search.filter(highlight=True, highlight_expires__lt=now)
        for product in products:
            product.save()