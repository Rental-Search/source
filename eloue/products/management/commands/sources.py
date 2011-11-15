# -*- coding: utf-8 -*-
import datetime
import inspect

from django.core.management.base import BaseCommand
from django.core import mail

import logbook


class DjangoMailHandler(logbook.MailHandler):

    def deliver(self, msg, recipients):
        """Delivers the given message to a list of recpients."""
        print inspect.getmembers(msg)
        mail.send_mail("importation error", msg.as_string(), self.from_addr, recipients)

handler = DjangoMailHandler("someone@example.com", ['other@example.com'],
                              format_string=logbook.handlers.MAIL_FORMAT_STRING, level='INFO', bubble = True, record_delta=datetime.timedelta(seconds=0))

log = logbook.Logger('eloue.rent.sources')

class Command(BaseCommand):
    help = "Update sources for affiliation."
    args = "[source_prefix source_prefix ...]"

    def handle(self, *args, **options):
        from eloue.products.sources import SourceManager
        log.info('Starting updating sources')
        
        try:
            manager = SourceManager(sources=args)
        except ImportError as e:
            log.exception("Source not found:\n{0}".format(e))
        except Exception as e:
            log.exception("Something bad happened:\n{0}".format(e))
        else:
            for source in manager.sources:
                log.info('Working on %s' % source.get_prefix())
                manager.remove_docs(source)
                with handler:
                    try:
                        manager.index_docs(source)
                    except Exception as e:
                        log.exception("Exception: {0}".format(e))
                        try:
                            manager.remove_docs(source)
                        except Exception as e1:
                            log.exception("Exception: {0}".format(e1))
                        continue