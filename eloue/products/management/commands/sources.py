# -*- coding: utf-8 -*-
import logbook

from django.core.management.base import BaseCommand

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
            return
        
        for source in manager.sources:
            log.info('Working on %s' % source.get_prefix())
            manager.remove_docs(source)
            try:
                manager.index_docs(source)
            except Exception as e:
                log.exception("Exception: {0}".format(e))
                try:
                    manager.remove_docs(source)
                except Exception as e1:
                    log.exception("Exception: {0}".format(e1))
                continue