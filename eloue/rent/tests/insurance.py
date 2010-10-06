# -*- coding: utf-8 -*-
from mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase

from eloue.rent.management.commands.billing import Command as BillingCommand
from eloue.rent.management.commands.reimbursement import Command as ReimbursementCommand

class InsuranceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'product']
    
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
        self.assertEquals(mock.return_value.method_calls[2][0], 'quit')
    
