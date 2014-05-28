# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal as D

from django.test import TransactionTestCase

from pyke.knowledge_engine import CanNotProve

from products.models import Product
from products.choices import UNIT
from rent.models import Booking
from rent.utils import timesince

class BookingPriceTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def setUp(self):
        self.product = Product.objects.get(pk=1)
    
    def test_calculate_hours_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(0, 240)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["4 "+ "minutes"]))
        self.assertEqual(timesince(ended_at, started_at), u', '.join(["0 "+ "minute"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('0.07'))
        self.assertEquals(unit, UNIT.HOUR)
    
    def test_calculate_week_end_price(self):
        started_at = datetime(2010, 9, 17, 9, 00)
        ended_at = started_at + timedelta(days=3)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["3 "+ "jours"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('36'))
        self.assertEquals(unit, UNIT.WEEK_END)
    
    def test_calculate_day_price(self):
        started_at = datetime(2010, 9, 20, 9, 00)
        ended_at = started_at + timedelta(days=4)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["4 "+ "jours"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('96'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_week_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=7)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["1 "+ "semaine"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('90'))
        self.assertEquals(unit, UNIT.WEEK)
    
    def test_calculate_two_weeks_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=14)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["2 "+ "semaines"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('135'))
        self.assertEquals(unit, UNIT.TWO_WEEKS)
    
    def test_calculate_leap_two_weeks(self):
        started_at = datetime(2011, 3, 4, 9)
        ended_at = started_at + timedelta(days=29)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["4 "+ "semaines", "1 " + "jour"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('279.64'))
        self.assertEquals(unit, UNIT.TWO_WEEKS)
        started_at = datetime(2011, 3, 4, 9)
        ended_at = started_at + timedelta(days=30)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["1 "+ "mois"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('289.29'))
        self.assertEquals(unit, UNIT.TWO_WEEKS)
    
    def test_calculate_leap_month(self):
        started_at = datetime(2011, 2, 4, 9)
        ended_at = started_at + timedelta(days=28)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["4 "+ "semaines"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('186.67'))
        self.assertEquals(unit, UNIT.MONTH)
    
    def test_calculate_month_price(self):
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=45)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["1 "+ "mois", "2 "+ "semaines", "1 " + "jour"]))
        unit, price = Booking.calculate_price(self.product, started_at, ended_at)
        self.assertEquals(price, D('300'))
        self.assertEquals(unit, UNIT.MONTH)
    
    def test_calculate_default_price(self):
        product = Product.objects.get(pk=2)
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=45)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["1 "+ "mois", "2 "+ "semaines", "1 " + "jour"]))
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('305.36'))
        self.assertEquals(unit, UNIT.TWO_WEEKS)
    
    def test_calculate_hourly_price(self):
        product = Product.objects.get(pk=2)
        started_at = datetime.now()
        ended_at = started_at + timedelta(seconds=360)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["6 "+ "minutes"]))
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('0.06'))
        self.assertEquals(unit, UNIT.HOUR)
    
    def test_calculate_two_week_price(self):
        product = Product.objects.get(pk=2)
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=18)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["2 "+ "semaines", "4 "+ "jours"]))
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('122.14'))
        self.assertEquals(unit, UNIT.TWO_WEEKS)
    
    def test_calculate_strict_day_price(self):
        product = Product.objects.get(pk=4)
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=1)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["1 "+ "jour"]))
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('450'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_strict_day_with_hours_price(self):
        product = Product.objects.get(pk=4)
        started_at = datetime.now()
        ended_at = started_at + timedelta(days=1, hours=4)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["1 "+ "jour", "4 "+ "heures"]))
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEqual(price, D('525'))
        self.assertEqual(unit, UNIT.DAY)
    
    def test_calculate_strict_with_hours_price(self):
        product = Product.objects.get(pk=4)
        started_at = datetime.now()
        ended_at = started_at + timedelta(hours=4)
        self.assertEqual(timesince(started_at, ended_at), u', '.join(["4 "+ "heures"]))
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEqual(price, D('450'))
        self.assertEqual(unit, UNIT.DAY)
        

class BookingSeasonTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def test_calculate_day_season(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 15)
        ended_at = started_at + timedelta(days=2)
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('22'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_over_season(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 15, 9, 0)
        ended_at = started_at + timedelta(days=14)
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('134.88'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_over_year(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 30, 9, 0)
        ended_at = started_at + timedelta(days=90)
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('720'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_on_start_terminal(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 6, 21, 9, 0)
        ended_at = started_at + timedelta(days=4)
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('44'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_on_end_terminal(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 20, 9, 0)
        ended_at = started_at + timedelta(days=3)
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEquals(price, D('31.88'))
        self.assertEquals(unit, UNIT.DAY)
    
    def test_calculate_just_at_the_end(self):
        product = Product.objects.get(pk=3)
        started_at = datetime(2010, 9, 22, 9, 0)
        ended_at = started_at + timedelta(days=1)
        unit, price = Booking.calculate_price(product, started_at, ended_at)
        self.assertEqual(unit, UNIT.DAY)
        self.assertEqual(price, D('14.00'))
        
        