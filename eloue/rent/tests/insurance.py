# -*- coding: utf-8 -*-
import csv
import datetime
from dateutil.relativedelta import relativedelta
from mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase

from eloue.rent.management.commands.billing import Command as BillingCommand
from eloue.rent.management.commands.reimbursement import Command as ReimbursementCommand
from eloue.rent.models import Booking, Sinister, BOOKING_STATE

class MockDate(datetime.date):
    @classmethod
    def today(cls):
        return datetime.date(2010, 8, 16)
    

class MockDelta(relativedelta):
    def __radd__(self, other):
        return datetime.date(2010, 8, 1)
    

class InsuranceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product', 'booking', 'sinister']
    
    def setUp(self):
        self.old_date = datetime.date
        datetime.date = MockDate
    
    @patch('dateutil.relativedelta.relativedelta')
    def test_billing_command(self, mock):
        mock.return_value = MockDelta()
        command = BillingCommand()
        command.handle()
        self.assertTrue(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].attachments), 1)
        csv_file = mail.outbox[0].attachments[0][1]
        csv_file.seek(0)
        i = 0
        for row in csv.reader(csv_file, delimiter='|'):
            booking = Booking.objects.get(pk=row[4])
            self.assertEquals(booking.booking_state, BOOKING_STATE.ENDED)
            i += 1
        self.assertEquals(i, 1)
        self.assertTrue(settings.INSURANCE_EMAIL in mail.outbox[0].to)
    
    @patch('dateutil.relativedelta.relativedelta')
    def test_reimbursement_command(self, mock):
        mock.return_value = MockDelta()
        command = ReimbursementCommand()
        command.handle()
        self.assertTrue(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].attachments), 1)
        csv_file = mail.outbox[0].attachments[0][1]
        csv_file.seek(0)
        i = 0
        for row in csv.reader(csv_file, delimiter='|'):
            booking = Booking.objects.get(pk=row[4])
            self.assertEquals(booking.booking_state, BOOKING_STATE.CANCELED)
            i += 1
        self.assertEquals(i, 2)
        self.assertTrue(settings.INSURANCE_EMAIL in mail.outbox[0].to)
    
    @patch('ftplib.FTP')
    def test_sinister_command(self, mock):
        import eloue.rent.management.commands.sinister as sinister
        reload(sinister) # It's loaded before we patch
        command = sinister.Command()
        command.handle()
        self.assertTrue(mock.called)
        self.assertEquals(mock.return_value.method_calls[0][0], 'login')
        self.assertEquals(mock.return_value.method_calls[1][0], 'storlines')
        csv_file = mock.return_value.method_calls[1][1][1]
        csv_file.seek(0)
        for row in csv.reader(csv_file, delimiter='|'):
            try:
                sinister = Sinister.objects.get(sinister_id=row[3])
            except Sinister.DoesNotExist:
                self.fail("A non-existing sinister is referenced")
        self.assertEquals(mock.return_value.method_calls[2][0], 'quit')
    
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
        i = 0
        for row in csv.reader(csv_file, delimiter='|'):
            booking = Booking.objects.get(pk=row[13])
            self.assertEquals(booking.booking_state, BOOKING_STATE.PENDING)
            i += 1
        self.assertEquals(i, 1)
        self.assertEquals(mock.return_value.method_calls[2][0], 'quit')
    
    def tearDown(self):
        datetime.date = self.old_date
    
