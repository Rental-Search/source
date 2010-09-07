# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from decimal import Decimal as D

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from eloue.accounts.models import Patron
from eloue.products.models import Product
from eloue.rent.models import Booking, PAYMENT_STATE

class BookingTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'product']
    
    def test_booking_created_at(self):
        booking = Booking.objects.create(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=3),
            total_price=10,
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
            total_price=10,
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
            total_price=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=1,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_negative_total_price(self):
        booking = Booking(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=3),
            total_price=-10,
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
            total_price=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertEqual(4, len(booking.pin))
        self.assertTrue(booking.pin.isdigit())
    

class BookingPayments(TestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'price']
    
    def setUp(self):
        self.product = Product.objects.get(pk=1)
    
    def test_calculate_hours_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(0, 240)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('1.2'))
    
    def test_calculate_week_end_price(self):
        started_at = datetime(2010, 9, 17, 9, 00)
        ended_at = started_at + timedelta(days=3)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('12'))
    
    def test_calculate_day_price(self):
        started_at = datetime(2010, 9, 20, 9, 00)
        ended_at = started_at + timedelta(days=4)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('28'))
    
    def test_calculate_week_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=7)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('35'))
    
    def test_calculate_two_weeks_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=14)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('56'))
    
    def test_calculate_leap_two_weeks(self):
        started_at = datetime(2011, 3, 4, 9)
        ended_at = started_at + timedelta(days=29)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('116'))
        started_at = datetime(2011, 3, 4, 9)
        ended_at = started_at + timedelta(days=30)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('120'))
    
    def test_calculate_leap_month(self):
        started_at = datetime(2011, 2, 4, 9)
        ended_at = started_at + timedelta(days=28)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('84'))
    
    def test_calculate_month_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=45)
        price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('135'))
    
