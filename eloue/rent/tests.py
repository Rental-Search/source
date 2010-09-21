# -*- coding: utf-8 -*-
import urllib
from datetime import datetime, timedelta

from decimal import Decimal as D

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from eloue.products.models import Product
from eloue.rent.models import Booking

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
    
    def test_long_booking(self):
        booking = Booking(
            started_at=datetime.now(),
            ended_at=datetime.now() + timedelta(days=90),
            total_price=10,
            booking_state=4,
            payment_state=1,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    

class BookingPriceTest(TestCase):
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
    
    def test_calculate_default_price(self):
        product = Product.objects.get(pk=2)
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=45)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('315'))
    
    def test_calculate_hourly_price(self):
        product = Product.objects.get(pk=2)
        started_at = datetime.now()
        ended_at = started_at + timedelta(seconds=360)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('3.6'))
    
    def test_calculate_two_week_price(self):
        product = Product.objects.get(pk=2)
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=18)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('126'))
    

class BookingSeasonTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'price']
    
    def test_calculate_day_season(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 15)
        ended_at = started_at + timedelta(days=2)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('20'))
    
    def test_calculate_over_season(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 15, 9, 0)
        ended_at = started_at + timedelta(days=14)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('126'))
    
    def test_calculate_over_year(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 30, 9, 0)
        ended_at = started_at + timedelta(days=90)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('720'))
    
    def test_calculate_on_start_terminal(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 6, 21, 9, 0)
        ended_at = started_at + timedelta(days=4)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('40'))
    
    def test_calculate_on_end_terminal(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 20, 9, 0)
        ended_at = started_at + timedelta(days=2)
        price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('20'))
    

class TestPaypalIPN(TestCase):
    def test_preapproval_ipn(self):
        data = {
            'approved':'true',
            'charset':'windows-1252',
            'currency_code':'EUR',
            'current_number_of_payments':'0',
            'current_period_attempts':'0',
            'current_total_amount_of_all_payments':'0.0',
            'date_of_month':'0',
            'day_of_week':'NO_DAY_SPECIFIED',
            'ending_date':'2010-09-16T11:28:20.0-07:00',
            'max_number_of_payments':'null',
            'max_total_amount_of_all_payments':'112.6',
            'notify_version':'UNVERSIONED',
            'payment_period':'0',
            'pin_type':'NOT_REQUIRED',
            'preapproval_key':'PA-2NS525738W954192E',
            'sender_email':'eloue_1283761258_per@tryphon.org',
            'starting_date':'2010-09-13T11:28:20.0-07:00',
            'status':'ACTIVE',
            'test_ipn':'1',
            'transaction_type':'Adaptive Payment PREAPPROVAL',
            'verify_sign':'An5ns1Kso7MWUdW4ErQKJJJ4qi4-Av.UjqUcxQnthRSekpwrT2LmjDTm'
        }
        response = self.client.post(reverse('preapproval_ipn'), urllib.urlencode(data), content_type='application/x-www-form-urlencoded; charset=windows-1252;')
        self.failUnlessEqual(response.status_code, 200)
    
    def test_pay_ipn(self):
        data = {
            'action_type':'PAY_PRIMARY',
            'cancel_url':'http://cancel.me',
            'charset':'windows-1252',
            'fees_payer':'PRIMARYRECEIVER',
            'ipn_notification_url':'http://www.postbin.org/1fi02go',
            'log_default_shipping_address_in_transaction':'false',
            'notify_version':'UNVERSIONED',
            'pay_key':'AP-1G646418FF723264N',
            'payment_request_date':'Mon Sep 13 02:31:12 PDT 2010',
            'return_url':'http://return.me',
            'reverse_all_parallel_payments_on_error':'false',
            'sender_email':'eloue_1283761258_per@tryphon.org',
            'status':'INCOMPLETE',
            'test_ipn':'1',
            'transaction[0].amount':'EUR 54.00',
            'transaction[0].id':'5G4772576R4998005',
            'transaction[0].id_for_sender_txn':'5UA91794R63363502',
            'transaction[0].is_primary_receiver':'true',
            'transaction[0].pending_reason':'NONE',
            'transaction[0].receiver':'sand_1266353156_biz@tryphon.org',
            'transaction[0].status':'Completed',
            'transaction[0].status_for_sender_txn':'Completed',
            'transaction[1].amount':'EUR 48.60',
            'transaction[1].is_primary_receiver':'false',
            'transaction[1].pending_reason':'NONE',
            'transaction[1].receiver':'eloue_1283761216_per@tryphon.org',
            'transaction_type':'Adaptive Payment PAY',
            'verify_sign':'ApZ7gM6YawE7YxcPuk9xgCNvybLAA.3oQL8gQFO3duXtJ-WfJ-dh1jJD'
        }
        response = self.client.post(reverse('pay_ipn'), urllib.urlencode(data), content_type='application/x-www-form-urlencoded; charset=windows-1252;')
        self.failUnlessEqual(response.status_code, 200)
    
