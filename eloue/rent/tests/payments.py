# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.core import mail
from django.test import TestCase

from mock import patch

from eloue.rent.models import Booking


class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return datetime.datetime(2010, 8, 19, 8, 0)
    

class MockBooking(Booking):
    @classmethod
    def objects(cls):
        return cls.objects
    

class PaymentsTest(TestCase):
    fixtures = ['patron', 'phones', 'address', 'price', 'product', 'booking', 'sinister']
    
    def setUp(self):
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime
    
    @patch.object(Booking, 'hold')
    def test_hold_command(self, mock_method):
        import eloue.rent.management.commands.hold as hold
        reload(hold)  # It's loaded before we patch
        command = hold.Command()
        command.handle()
        self.assertTrue(mock_method.called)
    
    def tearDown(self):
        datetime.datetime = self.old_datetime
    
