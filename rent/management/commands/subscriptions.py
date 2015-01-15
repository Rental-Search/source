# -*- coding: utf-8 -*-
import csv
import codecs
import logbook

from datetime import date, timedelta
from ftplib import FTP
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
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
        from accounts.choices import COUNTRY_CHOICES
        from rent.models import Booking
        log.info('Starting daily insurance subscriptions batch')
        csv_file = TemporaryFile()
        latin1csv_file = codecs.EncodedFile(csv_file, 'utf-8', 'latin1', 'ignore')
        writer = csv.writer(latin1csv_file, delimiter='|')
        period = (date.today() - timedelta(days=100))
        for booking in Booking.objects.pending().filter(created_at__year=period.year, created_at__month=period.month, created_at__day=period.day):
            row = SortedDict()
            row['Numéro locataire'] = booking.borrower.pk
            row['Login locataire'] = booking.borrower.username
            row['Adresse email'] = booking.borrower.email
            phones = tuple(booking.borrower.phones.all()[:1])
            phone = phones[0] if phones else None
            row['Téléphone locataire'] = phone
            row['Portable locataire'] = phone
            row['Nom'] = smart_str(booking.borrower.last_name.replace("\n", " ").replace("\r", " "))
            row[u'Prénom'] = smart_str(booking.borrower.first_name.replace("\n", " ").replace("\r", " "))
            for address in booking.borrower.addresses.all()[:1]:
                row['Adresse 1'] = smart_str(address.address1.replace("\n", " ").replace("\r", " "))
                row['Adresse 2'] = smart_str(address.address2.replace("\n", " ").replace("\r", " ")) if address.address2 else None
                row['Code postal'] = address.zipcode.replace("\n", " ").replace("\r", " ")
                row['Ville'] = smart_str(address.city.replace("\n", " ").replace("\r", " "))
                row['Pays'] = COUNTRY_CHOICES[address.country]
                break
            else:
                row['Adresse 1'] = \
                row['Adresse 2'] = \
                row['Code postal'] = \
                row['Ville'] = \
                row['Pays'] = \
            row['Numéro propriétaire'] = smart_str(booking.owner.pk)
            row['Login propriétaire'] = smart_str(booking.owner.username)
            row['Adresse email propriétaire'] = booking.owner.email
            phones = tuple(booking.owner.phones.all()[:1])
            phone = phones[0] if phones else None
            row['Téléphone propriétaire'] = phone
            row['Portable propriétaire'] = phone
            row['Nom propriétaire'] = smart_str(booking.owner.last_name.replace("\n", " ").replace("\r", " "))
            row[u'Prénom propriétaire'] = smart_str(booking.owner.first_name.replace("\n", " ").replace("\r", " "))
            for address in booking.owner.addresses.all()[:1]:
                row['Adresse 1 propriétaire'] = smart_str(address.address1.replace("\n", " ").replace("\r", " "))
                row['Adresse 2 propriétaire'] = smart_str(address.address2.replace("\n", " ").replace("\r", " ") if address.address2 else None)
                row['Code postal propriétaire'] = address.zipcode.replace("\n", " ").replace("\r", " ")
                row['Ville propriétaire'] = smart_str(address.city.replace("\n", " ").replace("\r", " "))
                row['Pays propriétaire'] = COUNTRY_CHOICES[address.country]
                break
            else:
                row['Adresse 1 propriétaire'] = \
                row['Adresse 2 propriétaire'] = \
                row['Code postal propriétaire'] = \
                row['Ville propriétaire'] = \
                row['Pays propriétaire'] = None
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = 500000 + booking.contract_id
            row['Date d\'effet de la location'] = booking.started_at.strftime("%Y%m%d")
            row[u'Numéro de commande'] = booking.uuid
            try:
                product = booking.product
                row['Type de produit'] = smart_str(product._get_category().name)
                row[u'Désignation'] = smart_str(product.description.replace("\n", " ").replace("\r", " "))
                row['Informations complémentaires produit'] = smart_str(product.summary.replace("\n", " ").replace("\r", " "))
            except ObjectDoesNotExist:
                row['Type de produit'] = \
                row[u'Désignation'] = \
                row['Informations complémentaires produit'] = None
            row['Prix de la location TTC'] = comma_separated(booking.total_amount)
            row['Montant de la Caution'] = comma_separated(booking.deposit_amount)
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            try:
                row[u'Prix de cession de l\'assurance HT'] = comma_separated(round(booking.insurance_fee, 2))
                row['Com. du partenaire'] = comma_separated(round(booking.insurance_commission, 2))
                row['Taxes assurance à 9%'] = comma_separated(round(booking.insurance_taxes, 2))
            except ObjectDoesNotExist:
                row[u'Prix de cession de l\'assurance HT'] = \
                row['Com. du partenaire'] = \
                row['Taxes assurance à 9%'] = None
            row['Cotisation TTC'] = comma_separated(round(booking.insurance_amount, 2))
            writer.writerow(row.values())
        latin1csv_file.seek(0)
        log.info('Uploading daily insurance subscriptions')
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        # set FTP PASSIVE mode; disabled by default
        ftp.set_pasv(getattr(settings, 'INSURANCE_FTP_PASSIVE_MODE', 0))
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR subscriptions-eloue-%s-%s-%s.csv" % (period.year, period.month, period.day), latin1csv_file)
        ftp.quit()
        log.info('Finished daily insurance subscriptions batch')
