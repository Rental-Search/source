# -*- coding: utf-8 -*-
import csv
import datetime
from mock import patch
from uuid import UUID

from django.conf import settings
from django.core import mail
from django.test import TestCase

from eloue.rent.management.commands.billing import Command as BillingCommand
from eloue.rent.management.commands.reimbursement import Command as ReimbursementCommand
from eloue.rent.models import Booking, BOOKING_STATE

class MockDate(datetime.date):
    @classmethod
    def today(cls):
        return datetime.date(2010, 8, 16)
    

class InsuranceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'booking']
    
    def setUp(self):
        self.old_date = datetime.date
        datetime.date = MockDate
    
    def test_billing_command(self):
        command = BillingCommand()
        command.handle()
        self.assertTrue(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].attachments), 1)
        self.assertTrue(settings.INSURANCE_EMAIL in mail.outbox[0].to)
    
    def test_reimbursement_command(self):
        command = ReimbursementCommand()
        command.handle()
        self.assertTrue(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].attachments), 1)
        self.assertTrue(settings.INSURANCE_EMAIL in mail.outbox[0].to)
    
    @patch('ftplib.FTP')
    def test_subscriptions_command(self, mock):
        import eloue.rent.management.commands.subscriptions as subscriptions
        reload(subscriptions) # It's loaded before we patch
        command = subscriptions.Command()
        command.handle()
        self.assertTrue(mock.called)
        self.assertEquals(mock.return_value.method_calls[0][0], 'login')
        self.assertEquals(mock.return_value.method_calls[1][0], 'storlines')
        csv_file = mock.return_value.method_calls[1][1][1]
        csv_file.seek(0)
        for i, row in enumerate(csv.reader(csv_file, delimiter='|')):
            booking = Booking.objects.get(pk=UUID(row[13]))
            self.assertEquals(booking.booking_state, BOOKING_STATE.PENDING)
            self.assertTrue(i <= 1)
        self.assertEquals(mock.return_value.method_calls[2][0], 'quit')
    
    def tearDown(self):
        datetime.date = self.old_date
    
