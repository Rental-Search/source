# -*- coding: utf-8 -*-
import csv
import logbook
import tempfile

from datetime import date
from ftplib import FTP

from django.core.management.base import BaseCommand

log = logbook.Logger('eloue.rent.reimbursement')

class Command(BaseCommand):
    help = "Send monthly insurance reimbursement"
    
    def handle(self, *args, **options):
        # FIXME : dumb date filter
        from django.conf import settings
        from eloue.rent.models import Booking, PAYMENT_STATE
        log.info('Starting monthly insurance reimbursement batch')
        csv_file, path = tempfile.mkstemp()
        writer = csv.writer(csv_file, delimiter='|')
        for booking in Booking.objects.canceled().filter(created_at__gte=date.today()):
            row = {}
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = booking.contract_id
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            row[u'Numéro de commande'] = booking.uuid
            row['Prix de la location TTC'] = booking.total_amount
            row['Date du remboursement'] = booking.canceled_at.strftime("%Y%m%d")
            if booking.payment_state <= PAYMENT_STATE.CANCELED:
                row['Type de remboursement'] = 'ANNULATION'
            elif booking.payment_state <= PAYMENT_STATE.REFUNDED:
                row['Type de remboursement'] = 'REMBOURSEMENT'
            else: # This should not happend
                log.warning("Monthly insurance reimbursement batch failed on booking #%s" % booking.uuid)
            row[u'Désignation'] = booking.product.description
            row['Prix de la location TTC'] = booking.total_amount
            row['Prix de cession HT'] = booking.insurance_fee
            row['Com. du partenaire'] = 0
            row['Taxes assurance à 9%'] = booking.insurance_taxes
            row['Cotisation TTC'] = booking.insurance_amount
            writer.writerow(row)
        log.info('Uploady monthly insurance reimbursement')
        ftp = FTP(settings.INSURANCE_FTP_HOST)
        ftp.login(settings.INSURANCE_FTP_USER, settings.INSURANCE_FTP_PASSWORD)
        if settings.INSURANCE_FTP_CWD:
            ftp.cwd(settings.INSURANCE_FTP_CWD)
        ftp.storlines("STOR " + csv_file.name, csv_file)
        ftp.quit()
        log.info('Finished monthly insurance reimbursement batch')
    
