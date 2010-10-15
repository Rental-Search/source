# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal as D

from django.test import TestCase

from eloue.products.models import Product
from eloue.rent.models import Booking

class BookingPriceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product']
    
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
    fixtures = ['patron', 'address', 'category', 'price', 'product']
    
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
    
