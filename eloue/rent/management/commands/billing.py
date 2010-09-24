# -*- coding: utf-8 -*-
import csv
import logbook
import tempfile

from datetime import date
from ftplib import FTP

from django.core.management.base import BaseCommand

log = logbook.Logger('eloue.rent.billing')

class Command(BaseCommand):
    help = "Send monthly insurance billing"
    
    def handle(self, *args, **options):
        # FIXME : dumb date filter and add logging
        from django.conf import settings
        from eloue.rent.models import Booking
        csv_file, path = tempfile.mkstemp()
        writer = csv.writer(csv_file, delimiter='|')
        for booking in Booking.objects.ended().filter(created_at__gte=date.today()):
            row = {}
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = booking.contract_id
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            row[u'Numéro de commande'] = booking.uuid
            row['Date d\'effet des garanties'] = booking.started_at.strftime("%Y%m%d")
            row[u'Désignation'] = booking.product.description
            row['Prix de la location TTC'] = booking.total_price
            # TODO : Missing fields 
            writer.writerow(row)
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR " + csv_file.name, csv_file)
        ftp.quit()
    
