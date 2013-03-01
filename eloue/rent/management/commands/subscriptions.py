# -*- coding: utf-8 -*-
import csv
import logbook

from datetime import date, timedelta
from ftplib import FTP
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

from eloue.decorators import activate_language

log = logbook.Logger('eloue.rent.subscriptions')

def comma_separated(number):
    return str(number).replace('.', ',')

class Command(BaseCommand):
    help = "Send daily insurance subscriptions"
    
    @activate_language
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
            row['Numéro locataire'] = booking.borrower.pk
            row['Login locataire'] = booking.borrower.username
            row['Adresse email'] = booking.borrower.email
            row['Téléphone locataire'] = booking.borrower.phones.all()[0]
            row['Portable locataire'] = booking.borrower.phones.all()[0]
            row['Nom'] = smart_str(booking.borrower.last_name.replace("\n", " ").replace("\r", " "))
            row[u'Prénom'] = smart_str(booking.borrower.first_name.replace("\n", " ").replace("\r", " "))
            address = booking.borrower.addresses.all()[0]
            row['Adresse 1'] = smart_str(address.address1.replace("\n", " ").replace("\r", " "))
            row['Adresse 2'] = smart_str(address.address2.replace("\n", " ").replace("\r", " ")) if address.address2 else None
            row['Code postal'] = address.zipcode.replace("\n", " ").replace("\r", " ")
            row['Ville'] = smart_str(address.city.replace("\n", " ").replace("\r", " "))
            row['Pays'] = COUNTRY_CHOICES[address.country]
            row['Numéro propriétaire'] = smart_str(booking.owner.pk)
            row['Login propriétaire'] = smart_str(booking.owner.username)
            row['Adresse email propriétaire'] = booking.owner.email
            row['Téléphone propriétaire'] = booking.owner.phones.all()[0]
            row['Portable propriétaire'] = booking.owner.phones.all()[0]
            row['Nom propriétaire'] = smart_str(booking.owner.last_name.replace("\n", " ").replace("\r", " "))
            row[u'Prénom propriétaire'] = smart_str(booking.owner.first_name.replace("\n", " ").replace("\r", " "))
            address = booking.owner.addresses.all()[0]
            row['Adresse 1 propriétaire'] = smart_str(address.address1.replace("\n", " ").replace("\r", " "))
            row['Adresse 2 propriétaire'] = smart_str(address.address2.replace("\n", " ").replace("\r", " ") if address.address2 else None)
            row['Code postal propriétaire'] = address.zipcode.replace("\n", " ").replace("\r", " ")
            row['Ville propriétaire'] = smart_str(address.city.replace("\n", " ").replace("\r", " "))
            row['Pays propriétaire'] = COUNTRY_CHOICES[address.country]
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = 500000 + booking.contract_id
            row['Date d\'effet de la location'] = booking.started_at.strftime("%Y%m%d")
            row[u'Numéro de commande'] = booking.uuid
            row['Type de produit'] = smart_str(booking.product.category.name)
            row[u'Désignation'] = smart_str(booking.product.description.replace("\n", " ").replace("\r", " "))
            row['Informations complémentaires produit'] = smart_str(booking.product.summary.replace("\n", " ").replace("\r", " "))
            row['Prix de la location TTC'] = comma_separated(booking.total_amount)
            row['Montant de la Caution'] = comma_separated(booking.deposit_amount)
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            row[u'Prix de cession de l\'assurance HT'] = comma_separated(round(booking.insurance_fee, 2))
            row['Com. du partenaire'] = comma_separated(round(booking.insurance_commission, 2))
            row['Taxes assurance à 9%'] = comma_separated(round(booking.insurance_taxes, 2))
            row['Cotisation TTC'] = comma_separated(round(booking.insurance_amount, 2))
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
        ftp.storlines("STOR subscriptions-eloue-%s-%s.csv" % (period.month, period.day), latin1csv_file)
        ftp.quit()
        log.info('Finished daily insurance subscriptions batch')
    
