# -*- coding: utf-8 -*-
import datetime

from django.db import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError

from eloue.products.models import Product, Review, Price, StandardPrice, SeasonalPrice

class ProductTest(TestCase):
    fixtures = ['patron', 'address', 'category']
    
    def test_product_creation(self):
        product = Product(
            summary="Perceuse visseuse Philips",
            deposit=250,
            description=u"Engrenage planétaire à haute performance 2 vitesses : durée de vie supérieure, transmission optimale, fonctionnement régulier.",
            address_id=1,
            quantity=1,
            category_id=1,
            owner_id=1
        )
        product.save()
    
    def test_product_owner_address(self):
        product = Product(
            summary="Perceuse visseuse Philips",
            deposit=250,
            description=u"Engrenage planétaire à haute performance 2 vitesses : durée de vie supérieure, transmission optimale, fonctionnement régulier.",
            address_id=1,
            quantity=1,
            category_id=1,
            owner_id=2
        )
        self.assertRaises(ValidationError, product.full_clean)
    

class ReviewTest(TestCase):
    fixtures = ['patron', 'address', 'product']
    
    def test_score_values_negative(self):
        review = Review(score=-1.0, product_id=1, description='Incorrect')
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = Review(score=2.0, product_id=1, description='Parfait')
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = Review(score=0.5, product_id=1, description='Correct')
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    

class PriceTest(TestCase):
    fixtures = ['patron', 'address', 'product']
    
    def test_amount_values_negative(self):
        price = Price(amount=-1, product_id=1, currency='EUR')
        self.assertRaises(ValidationError, price.full_clean)
    
    def test_amount_values_positive(self):
        try:
            price = Price(amount=20, product_id=1, currency='EUR')
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
        standard_price = StandardPrice.objects.create(unit=1, amount=10, product_id=1, currency='EUR')
        product = Product.objects.get(pk=1)
        self.assertTrue(standard_price in product.standardprice.all())
    
    def test_pricing_uniqueness(self):
        StandardPrice.objects.create(unit=1, amount=10, product_id=1, currency='EUR')
        self.assertRaises(IntegrityError, StandardPrice.objects.create, unit=1, amount=20, product_id=1)
    

class SeasonalPriceTest(TestCase):
    fixtures = ['patron', 'address', 'product']
    
    def setUp(self):
        from django.db import connection
        self.isolation_level = connection.isolation_level
        connection._set_isolation_level(0)
    
    def tearDown(self):
        from django.db import connection
        connection._set_isolation_level(self.isolation_level)
    
    def test_product_pricing(self):
        seasonal_price = SeasonalPrice.objects.create(
            name='Haute saison',
            product_id=1,
            amount=30,
            currency='EUR',
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3)
        )
        product = Product.objects.get(pk=1)
        self.assertTrue(seasonal_price in product.seasonalprice.all())
    
    def test_pricing_uniqueness(self):
        from django.db import connection
        self.assertEquals(connection.isolation_level, 0)
        SeasonalPrice.objects.create(
            name='Haute saison',
            product_id=1,
            amount=20,
            currency='EUR',
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3)
        )
        self.assertRaises(IntegrityError, SeasonalPrice.objects.create, 
            name='Haute saison',
            product_id=1,
            amount=25,
            currency='EUR',
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3)
        )
    
    def test_wrong_start_and_end_date(self):
        seasonal_price = SeasonalPrice(
            name='Haute saison',
            product_id=1,
            amount=40,
            currency='EUR',
            started_at=datetime.datetime.now() + datetime.timedelta(days=3),
            ended_at=datetime.datetime.now()
        )
        self.assertRaises(ValidationError, seasonal_price.full_clean)
    
    def test_correct_start_and_end_date(self):
        seasonal_price = SeasonalPrice(
            name='Haute saison',
            product_id=1,
            currency='EUR',
            amount=60,
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3)
        )
        try:
            seasonal_price.full_clean()
        except ValidationError, e:
            self.fail(e)
    
