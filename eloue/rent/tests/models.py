# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal as D

from django.core.exceptions import ValidationError
from django.test import TestCase

from eloue.rent.models import Booking


class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return datetime.datetime(2010, 8, 15, 9, 0)
    

class BookingTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def setUp(self):
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime
    
    def test_booking_created_at(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertEquals(booking.created_at, datetime.datetime.now())
    
    def test_start_and_end_date(self):
        booking = Booking(
            started_at=datetime.datetime.now() + datetime.timedelta(days=3),
            ended_at=datetime.datetime.now(),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_same_owner_and_borrower(self):
        booking = Booking(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=1,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_negative_total_amount(self):
        booking = Booking(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            total_amount=-10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_pin_code(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertEqual(4, len(booking.pin))
        self.assertTrue(booking.pin.isdigit())
    
    def test_long_booking(self):
        booking = Booking(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=90),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_insurance_price(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=80),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=4
        )
        self.assertEquals(booking.insurance_amount, D('0.58860'))
    
    def test_no_insurance(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=80),
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=3
        )
        self.assertEquals(booking.insurance_amount, D(0))
    
    def tearDown(self):
        datetime.datetime = self.old_datetime
    
