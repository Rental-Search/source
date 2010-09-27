# -*- coding: utf-8 -*-
import csv
import logbook

from dateutil.relativedelta import relativedelta
from datetime import date
from ftplib import FTP
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand

log = logbook.Logger('eloue.rent.billing')

class Command(BaseCommand):
    help = "Send monthly insurance billing"
    
    def handle(self, *args, **options):
        from django.conf import settings
        from eloue.rent.models import Booking
        log.info('Starting monthly insurance billing batch')
        csv_file = TemporaryFile()
        writer = csv.writer(csv_file, delimiter='|')
        period = (date.today() - relativedelta(months=1))
        for booking in Booking.objects.ended().filter(created_at__year=period.year, created_at__month=period.month):
            row = {}
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = booking.contract_id
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            row[u'Numéro de commande'] = booking.uuid
            row['Date d\'effet des garanties'] = booking.started_at.strftime("%Y%m%d")
            row[u'Désignation'] = booking.product.description
            row['Prix de la location TTC'] = booking.total_amount
            row['Prix de cession HT'] = booking.insurance_fee
            row['Com. du partenaire'] = booking.insurance_commission
            row['Taxes assurance à 9%'] = booking.insurance_taxes
            row['Cotisation TTC'] = booking.insurance_amount
            writer.writerow(row)
        log.info('Uploading monthly insurance billing')
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR " + csv_file.name, csv_file)
        ftp.quit()
        log.info('Finished monthly insurance reimbursement batch')
    
