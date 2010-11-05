# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from eloue.products.models import Product, Price


class PriceTest(TestCase):
    fixtures = ['patron', 'address', 'product']
    
    def test_amount_values_negative(self):
        price = Price(amount=-1, product_id=1, unit=1, currency='EUR')
        self.assertRaises(ValidationError, price.full_clean)
    
    def test_amount_values_positive(self):
        try:
            price = Price(amount=20, product_id=4, unit=0, currency='EUR')
            price.full_clean()
        except ValidationError, e:
            self.fail(e)
    

class StandardPriceTest(TestCase):
    fixtures = ['patron', 'address', 'product']
    
    def setUp(self):
        from django.db import connection
        self.isolation_level = connection.isolation_level
        connection._set_isolation_level(0)
    
    def tearDown(self):
        from django.db import connection
        connection._set_isolation_level(self.isolation_level)
    
    def test_product_pricing(self):
        standard_price = Price.objects.create(unit=1, amount=10, product_id=1, currency='EUR')
        product = Product.objects.get(pk=1)
        self.assertTrue(standard_price in product.prices.all())
    
    def test_pricing_uniqueness(self):
        Price.objects.create(unit=1, amount=10, product_id=1, currency='EUR')
        self.assertRaises(IntegrityError, Price.objects.create, unit=1, amount=20, product_id=1)
    

class SeasonalPriceTest(TestCase):
    fixtures = ['patron', 'address', 'product', 'booking']
    
    def setUp(self):
        from django.db import connection
        self.isolation_level = connection.isolation_level
        connection._set_isolation_level(0)
    
    def tearDown(self):
        from django.db import connection
        connection._set_isolation_level(self.isolation_level)
    
    def test_product_pricing(self):
        seasonal_price = Price.objects.create(
            name='Haute saison',
            product_id=1,
            amount=30,
            unit=1,
            currency='EUR',
            started_at=datetime.date.today(),
            ended_at=datetime.date.today() + datetime.timedelta(days=3)
        )
        product = Product.objects.get(pk=1)
        self.assertTrue(seasonal_price in product.prices.all())
    
    def test_pricing_uniqueness(self):
        from django.db import connection
        self.assertEquals(connection.isolation_level, 0)
        Price.objects.create(
            name='Haute saison',
            product_id=1,
            amount=20,
            unit=1,
            currency='EUR',
            started_at=datetime.date.today(),
            ended_at=datetime.date.today() + datetime.timedelta(days=3)
        )
        self.assertRaises(IntegrityError, Price.objects.create,
            name='Haute saison',
            product_id=1,
            amount=25,
            unit=1,
            currency='EUR',
            started_at=datetime.date.today(),
            ended_at=datetime.date.today() + datetime.timedelta(days=3)
        )
    
