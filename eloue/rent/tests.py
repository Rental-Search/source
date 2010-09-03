# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from eloue.accounts.models import Patron
from eloue.rent.models import Booking, PAYMENT_STATE

class BookingTest(TestCase):
    fixtures = ['patron', 'address', 'product']
    
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
    
    def test_start_and_end_date(self):
        booking = Booking(
            started_at=datetime.datetime.now() + datetime.timedelta(days=3),
            ended_at=datetime.datetime.now(),
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
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
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
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
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
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
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
    fixtures = ['patron', 'address', 'product']
    
    def setUp(self):
        Patron.objects.filter(pk=2).update(email='sand_1266353091_per@tryphon.org')
    
    def test_booking_preapproval(self):
        booking = Booking.objects.create(
            started_at = datetime.datetime.now(),
            ended_at = datetime.datetime.now() + datetime.timedelta(days=3),
            total_price = 10,
            owner_id = 1,
            borrower_id = 2,
            product_id = 1,
            currency = 'EUR'
        )
        booking.preapproval(cancel_url="http://cancel.me", return_url="http://return.me", ip_address='192.168.0.12')
        self.assertTrue(booking.preapproval_key)
        self.assertEquals(booking.payment_state, PAYMENT_STATE.AUTHORIZED)
    
    def test_booking_hold(self):
        booking = Booking.objects.create(
            started_at = datetime.datetime.now(),
            ended_at = datetime.datetime.now() + datetime.timedelta(days=3),
            total_price = 10,
            owner_id = 1,
            borrower_id = 2,
            product_id = 1,
            currency = 'EUR'
        )
        booking.preapproval(cancel_url="http://cancel.me", return_url="http://return.me", ip_address='192.168.0.12')
        self.assertTrue(booking.preapproval_key)
        self.assertEquals(booking.payment_state, PAYMENT_STATE.AUTHORIZED)
        #"https://www.sandbox.paypal.com/webscr?cmd=_ap-preapproval&preapprovalkey=%s" % booking.preapproval_key
        #booking.hold(cancel_url="http://cancel.me", return_url="http://return.me")
        #self.assertTrue(booking.pay_key)
        #self.assertEquals(booking.payment_state, PAYMENT_STATE.HOLDED)
    
