# -*- coding: utf-8 -*-
import csv
import logbook
from tempfile import TemporaryFile

from dateutil.relativedelta import relativedelta
from datetime import date

from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

from eloue.decorators import activate_language

log = logbook.Logger('eloue.rent.reimbursement')


class Command(BaseCommand):
    help = "Send monthly insurance reimbursement"
    
    @activate_language
    def handle(self, *args, **options):
        from django.conf import settings
        from rent.models import Booking
        log.info('Starting monthly insurance reimbursement batch')
        csv_file = TemporaryFile()
        writer = csv.writer(csv_file, delimiter='|')
        period = (date.today() - relativedelta(months=1))
        for booking in Booking.objects.canceled().filter(canceled_at__year=period.year, canceled_at__month=period.month):
            row = SortedDict()
            row['Numéro police'] = settings.POLICY_NUMBER
            row['Numéro partenaire'] = settings.PARTNER_NUMBER
            row['Numéro contrat'] = booking.contract_id
            row[u'Durée de garantie'] = (booking.ended_at - booking.started_at).days
            row[u'Numéro de commande'] = booking.uuid
            row['Prix de la location TTC'] = booking.total_amount
            row['Date du remboursement'] = booking.canceled_at.strftime("%Y%m%d")
            if booking.state == Booking.STATE.CANCELED:
                row['Type de remboursement'] = 'ANNULATION'
            elif booking.state == Booking.STATE.REFUNDED:
                row['Type de remboursement'] = 'REMBOURSEMENT'
            row[u'Désignation'] = smart_str(booking.product.description)
            row['Prix de la location TTC'] = booking.total_amount
            row['Prix de cession HT'] = booking.insurance_fee
            row['Com. du partenaire'] = booking.insurance_commission
            row['Taxes assurance à 9%'] = booking.insurance_taxes
            row['Cotisation TTC'] = booking.insurance_amount
            writer.writerow(row.values())
        log.info('Send monthly insurance reimbursement by mail')
        email = EmailMessage('Fichier remboursement e-loue.com',
            'Ci-joint le fichier de remboursement du %s/%s' % (
                period.month, period.year
            ), 'ops@e-loue.com',
            [settings.INSURANCE_EMAIL])
        email.attach('remboursement-eloue-%s-%s.csv' %
            (period.month, period.year), csv_file)
        email.send()
        log.info('Finished monthly insurance reimbursement batch')
    
