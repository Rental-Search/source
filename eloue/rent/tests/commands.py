# -*- coding: utf-8 -*-
import datetime

from django.test import TransactionTestCase

from mock import patch

from rent.models import Booking
from rent.choices import BOOKING_STATE


class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return datetime.datetime(2010, 8, 19, 9, 0)
    

class MockBooking(Booking):
    @classmethod
    def objects(cls):
        return cls.objects
    

class PaymentsTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'phones', 'address', 'price', 'product', 'booking', 'sinister']
    
    def setUp(self):
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime
    
    @patch.object(Booking, 'activate')
    def test_ongoing_command(self, mock_method):
        import rent.management.commands.ongoing as ongoing
        reload(ongoing)  # It's loaded before we patch
        booking1 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608dab6d") # non pay
        booking2 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608dab66") # paypal pay
        booking3 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608d9a7e")
        self.assertTrue(booking1.state, BOOKING_STATE.PENDING)
        self.assertTrue(booking2.state, BOOKING_STATE.PENDING)
        self.assertTrue(booking3.state, BOOKING_STATE.PENDING)
        command = ongoing.Command()
        command.handle()
        self.assertTrue(mock_method.called)
        self.assertTrue(booking1.state, BOOKING_STATE.PENDING)
        self.assertTrue(booking2.state, BOOKING_STATE.ONGOING)
        self.assertTrue(booking3.state, BOOKING_STATE.PENDING)
    
    def test_ended_command(self):
        import rent.management.commands.ended as ended
        reload(ended)
        booking1 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608dab66") #non pay
        booking2 = Booking.objects.get(uuid="349ce9ba628abfdfc9cb3a72608d9a7d") #paypal pay
        self.assertTrue(booking1.state, BOOKING_STATE.ONGOING)
        self.assertTrue(booking2.state, BOOKING_STATE.ONGOING)
        command = ended.Command()
        command.handle()
        self.assertTrue(booking1.state, BOOKING_STATE.ENDED)
        self.assertTrue(booking2.state, BOOKING_STATE.ENDED)
        
    def tearDown(self):
        datetime.datetime = self.old_datetime
    
