# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase

from eloue.accounts.models import Patron
from eloue.rent.models import Booking

class BookingTest(TestCase):
    fixtures = ['patron']
    def test_booking_created_at(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            total_price=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertTrue(booking.created_at <= datetime.datetime.now())
        created_at = booking.created_at
        booking.save()
        self.assertEquals(booking.created_at, created_at)
    
