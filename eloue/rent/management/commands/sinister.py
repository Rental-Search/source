# -*- coding: utf-8 -*-
import csv
import logbook

from datetime import date, timedelta
from ftplib import FTP
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand
from django.utils.datastructures import SortedDict

log = logbook.Logger('eloue.rent.sinister')

class Command(BaseCommand):
    help = "Send daily insurance sinisters"
    
    def handle(self, *args, **options):
        from django.conf import settings
        from eloue.rent.models import Sinister
        log.info('Starting daily insurance sinisters batch')
        csv_file = TemporaryFile()
        writer = csv.writer(csv_file, delimiter='|')
        period = (date.today() - timedelta(days=1))
        for sinister in Sinister.objects.filter(created_at__year=period.year, created_at__month=period.month, created_at__day=period.day):
            row = SortedDict()
            row['Login locataire'] = sinister.booking.borrower.username
            row['Adresse email'] = sinister.booking.borrower.email
            row[u'Numéro de téléphone'] = sinister.booking.borrower.phones.all()[0]
            row[u'Numéro du sinistre'] = sinister.sinister_id
            row['Date de survenance du sinistre'] = sinister.created_at.strftime("%Y%m%d")
            row['Nature du sinistre'] = 'bris'
            row['Description des circonstances'] = sinister.description
            row[u'Numéro police'] = settings.POLICY_NUMBER
            row[u'Numéro partenaire'] = settings.PARTNER_NUMBER
            row[u'Numéro contrat'] = sinister.booking.contract_id
            row['Date d\'effet des garanties'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = sinister.booking.contract_id
            row['Date d\'effet des garanties'] = sinister.booking.started_at.strftime("%Y%m%d")
            row[u'Numéro de commande'] = sinister.booking.uuid
            row[u'Type de produit'] = sinister.booking.category.name
            row['Montant de la Caution'] = sinister.booking.deposit_amount
            row['Prix de la location TTC'] = sinister.booking.total_amount
            writer.writerow(row.values())
        log.info('Uploading daily insurance subscriptions')
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR sinistre-eloue-%s-%s" % (period.month, period.day), csv_file)
        ftp.quit()
        log.info('Finished daily insurance sinisters batch')
    
