# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from eloue.rent.models import Booking

class BookingTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'product']
    
    def test_booking_created_at(self):
        booking = Booking.objects.create(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=3),
            total_amount=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertTrue(booking.created_at <= datetime.now())
        created_at = booking.created_at
        booking.save()
        self.assertEquals(booking.created_at, created_at)
    
    def test_start_and_end_date(self):
        booking = Booking(
            started_at=datetime.now() + timedelta(days=3),
            ended_at=datetime.now(),
            total_amount=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_same_owner_and_borrower(self):
        booking = Booking(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=3),
            total_amount=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=1,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_negative_total_amount(self):
        booking = Booking(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=3),
            total_amount=-10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_pin_code(self):
        booking = Booking.objects.create(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=3),
            total_amount=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertEqual(4, len(booking.pin))
        self.assertTrue(booking.pin.isdigit())
    
    def test_long_booking(self):
        booking = Booking(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=90),
            total_amount=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
