# -*- coding: utf-8 -*-
from datetime import datetime
from mock import Mock

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase

from eloue.rent.management.commands.billing import Command as BillingCommand
from eloue.rent.management.commands.reimbursement import Command as ReimbursementCommand
from eloue.rent.models import Booking

class InsuranceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'product']
    
    def setUp(self):
        import ftplib
        self.mock = Mock()
        ftplib.FTP = self.mock
    
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
    
    def test_subscriptions_command(self):
        from eloue.rent.management.commands.subscriptions import Command as SubscriptionsCommand
        command = SubscriptionsCommand()
        command.handle()
        self.assertTrue(self.mock.called)
        self.assertEquals(self.mock.return_value.method_calls[0][0], 'login')
        self.assertEquals(self.mock.return_value.method_calls[1][0], 'storlines')
        self.assertEquals(self.mock.return_value.method_calls[2][0], 'quit')
    
    def tearDown(self):
        self.mock.reset_mock()
    
