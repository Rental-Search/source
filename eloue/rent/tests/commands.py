# -*- coding: utf-8 -*-
import datetime

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
    fixtures = ['category', 'patron', 'phones', 'address', 'price', 'product', 'booking', 'sinister']
    
    def setUp(self):
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime
    
    @patch.object(Booking, 'hold')
    def test_ongoing_command(self, mock_method):
        import eloue.rent.management.commands.ongoing as ongoing
        reload(ongoing)  # It's loaded before we patch
        booking1 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608dab6d") # non pay
        booking2 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608dab66") # paypal pay
        self.assertTrue(booking1.state, Booking.STATE.PENDING)
        self.assertTrue(booking2.state, Booking.STATE.PENDING)
        command = ongoing.Command()
        command.handle()
        self.assertTrue(mock_method.called)
        self.assertTrue(booking1.state, Booking.STATE.ONGOING)
        self.assertTrue(booking2.state, Booking.STATE.ONGOING)
    
    def test_ended_command(self):
        import eloue.rent.management.commands.ended as ended
        reload(ended)
        booking1 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608dab66") #non pay
        booking2 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608d9a7d") #paypal pay
        self.assertTrue(booking1.state, Booking.STATE.ONGOING)
        self.assertTrue(booking2.state, Booking.STATE.ONGOING)
        command = ended.Command()
        command.handle()
        self.assertTrue(booking1.state, Booking.STATE.ENDED)
        self.assertTrue(booking2.state, Booking.STATE.ENDED)
        
    def tearDown(self):
        datetime.datetime = self.old_datetime
    
