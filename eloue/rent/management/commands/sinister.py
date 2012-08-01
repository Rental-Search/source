# -*- coding: utf-8 -*-
import csv
import logbook

from datetime import date, timedelta
from ftplib import FTP
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str
from django.db.models import Q

from eloue.decorators import activate_language

log = logbook.Logger('eloue.rent.sinister')

def comma_separated(number):
    return str(number).replace('.', ',')

class Command(BaseCommand):
    help = "Send daily insurance sinisters"
    
    @activate_language
    def handle(self, *args, **options):
        from django.conf import settings
        from eloue.rent.models import Sinister
        log.info('Starting daily insurance sinisters batch')
        csv_file = TemporaryFile()
        writer = csv.writer(csv_file, delimiter='|')
        period = (date.today() - timedelta(days=1))
        for sinister in Sinister.objects.filter(
            ~Q(product__owner__is_professional=True), 
            product__carproduct=None, product__realestateproduct=None, 
            created_at__year=period.year, created_at__month=period.month, 
            created_at__day=period.day, product__category__need_insurance=True):
            row = SortedDict()
            row['Login locataire'] = sinister.booking.borrower.username
            row['Adresse email'] = sinister.booking.borrower.email
            phones = sinister.booking.borrower.phones.all()
            if phones:
                row[u'Numéro de téléphone'] = phones[0]
            else:
                row[u'Numéro de téléphone'] = None
            row[u'Numéro du sinistre'] = sinister.sinister_id
            row['Date de survenance du sinistre'] = sinister.created_at.strftime("%Y%m%d")
            row['Nature du sinistre'] = 'bris'
            row['Description des circonstances'] = smart_str(sinister.description)
            row[u'Numéro police'] = settings.POLICY_NUMBER
            row[u'Numéro partenaire'] = settings.PARTNER_NUMBER
            row[u'Numéro contrat'] = sinister.booking.contract_id
            row['Date d\'effet des garanties'] = sinister.booking.started_at.strftime("%Y%m%d")
            row[u'Numéro de commande'] = sinister.booking.uuid
            row[u'Type de produit'] = smart_str(sinister.booking.product.category.name)
            row['Montant de la Caution'] = comma_separated(sinister.booking.deposit_amount)
            row['Prix de la location TTC'] = comma_separated(sinister.booking.total_amount)
            writer.writerow(row.values())
        csv_file.seek(0)
        latin1csv_file = TemporaryFile()
        for line in csv_file:
            latin1csv_file.write(line.decode('utf-8').encode('latin1', 'ignore'))
        latin1csv_file.seek(0)
        log.info('Uploading daily insurance subscriptions')
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR sinistre-eloue-%s-%s" % (period.month, period.day), latin1csv_file)
        ftp.quit()
        log.info('Finished daily insurance sinisters batch')
    
