# -*- coding: utf-8 -*-
import csv
import tempfile

from datetime import date
from ftplib import FTP

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send daily insurance subscriptions"
    
    def handle(self, *args, **options):
        # FIXME : dumb date filter and add logging
        from django.conf import settings
        from eloue.accounts.models import COUNTRY_CHOICES
        from eloue.rent.models import Booking
        csv_file, path = tempfile.mkstemp()
        writer = csv.writer(csv_file, delimiter='|')
        for booking in Booking.objects.pending().filter(created_at__gte=date.today()):
            row = {}
            row['Login locataire'] = booking.borrower.username
            row['Adresse email'] = booking.borrower.email
            row['Nom'] = booking.borrower.last_name
            row[u'Prénom'] = booking.borrower.first_name
            row['Adresse 1'] = booking.borrower.addresses[0].address1
            row['Adresse 2'] = booking.borrower.addresses[0].address2
            row['Code postal'] = booking.borrower.addresses[0].zipcode
            row['Ville'] = booking.borrower.addresses[0].city
            row['Pays'] = COUNTRY_CHOICES[booking.borrower.addresses[0].country]
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = booking.contract_id
            row['Date d\'effet des garanties'] = booking.started_at.strftime("%Y%m%d")
            row[u'numéro de commande'] = booking.uuid
            row[u'Désignation'] = booking.product.description
            row['Prix de la location TTC'] = booking.total_price
            row['Montant de la Caution'] = booking.deposit
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            # TODO : Missing fields 
            writer.writerow(row)
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR " + csv_file.name, csv_file)
        ftp.quit()
    
