# -*- coding: utf-8 -*-
import logbook

from django.core.management.base import BaseCommand

log = logbook.Logger('eloue.rent.sources')


class Command(BaseCommand):
    help = "Update sources for affiliation"
    
    def handle(self, *args, **options):
        from eloue.products.sources import SourceManager
        log.info('Starting updating sources')
        manager = SourceManager()
        manager.remove_docs()
        manager.index_docs()
    
