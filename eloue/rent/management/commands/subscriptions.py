# -*- coding: utf-8 -*-
import csv
import logbook

from datetime import date, timedelta
from ftplib import FTP
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

log = logbook.Logger('eloue.rent.subscriptions')


class Command(BaseCommand):
    help = "Send daily insurance subscriptions"
    
    def handle(self, *args, **options):
        from django.conf import settings
        from eloue.accounts.models import COUNTRY_CHOICES
        from eloue.rent.models import Booking
        log.info('Starting daily insurance subscriptions batch')
        csv_file = TemporaryFile()
        writer = csv.writer(csv_file, delimiter='|')
        period = (date.today() - timedelta(days=1))
        for booking in Booking.objects.pending().filter(created_at__year=period.year, created_at__month=period.month, created_at__day=period.day):
            row = SortedDict()
            row['Login locataire'] = booking.borrower.username
            row['Adresse email'] = booking.borrower.email
            row['Nom'] = smart_str(booking.borrower.last_name)
            row[u'Prénom'] = smart_str(booking.borrower.first_name)
            address = booking.borrower.addresses.all()[0]
            row['Adresse 1'] = smart_str(address.address1)
            row['Adresse 2'] = smart_str(address.address2) if address.address2 else None
            row['Code postal'] = address.zipcode
            row['Ville'] = smart_str(address.city)
            row['Pays'] = COUNTRY_CHOICES[address.country]
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = booking.contract_id
            row['Date d\'effet des garanties'] = booking.started_at.strftime("%Y%m%d")
            row[u'Numéro de commande'] = booking.uuid
            row[u'Désignation'] = smart_str(booking.product.description)
            row['Prix de la location TTC'] = booking.total_amount
            row['Montant de la Caution'] = booking.deposit_amount
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            row[u'Prix de cession de l\'assurance HT'] = booking.insurance_fee
            row['Com. du partenaire'] = booking.insurance_commission
            row['Taxes assurance à 9%'] = booking.insurance_taxes
            row['Cotisation TTC'] = booking.insurance_amount
            writer.writerow(row.values())
        log.info('Uploading daily insurance subscriptions')
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR subscriptions-eloue-%s-%s" % (period.month, period.day), csv_file)
        ftp.quit()
        log.info('Finished daily insurance subscriptions batch')
    
