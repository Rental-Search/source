# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase

from eloue.products.models import Product, ProductReview, PatronReview, Price

class ProductTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product']
    
    def test_product_creation(self):
        product = Product(
            summary="Perceuse visseuse Philips",
            deposit_amount=250,
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
            deposit_amount=250,
            description=u"Engrenage planétaire à haute performance 2 vitesses : durée de vie supérieure, transmission optimale, fonctionnement régulier.",
            address_id=1,
            quantity=1,
            category_id=1,
            owner_id=2
        )
        self.assertRaises(ValidationError, product.full_clean)
    
    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=['perceuse-visseuse-philips', 1]))
        self.assertEqual(response.status_code, 200)
    
    def test_product_detail_redirect(self):
        response = self.client.get(reverse('product_detail', args=['perceuse-visseuse', 1]))
        self.assertRedirects(response, reverse('product_detail', args=['perceuse-visseuse-philips', 1]), status_code=301)
    

class ProductReviewTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product', 'booking']
    
    def test_score_values_negative(self):
        review = ProductReview(score=-1.0, product_id=1, description='Incorrect', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = ProductReview(score=2.0, product_id=1, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = ProductReview(score=0.5, product_id=1, description='Correct', reviewer_id=2)
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    
    def test_owner_review(self):
        review = ProductReview(score=2.0, product_id=1, description='Parfait', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_booking_review(self):
        review = ProductReview(score=2.0, product_id=2, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    

class PatronReviewTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product', 'booking']
    
    def test_score_values_negative(self):
        review = PatronReview(score=-1.0, patron_id=1, description='Incorrect', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = PatronReview(score=2.0, patron_id=1, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = PatronReview(score=0.5, patron_id=1, description='Correct', reviewer_id=2)
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    
    def test_patron_review(self):
        review = PatronReview(score=2.0, patron_id=1, description='Correct', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_booking_review(self):
        review = PatronReview(score=2.0, patron_id=2, description='Correct', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    

class PriceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product']
    
    def test_amount_values_negative(self):
        price = Price(amount=-1, product_id=1, unit=1, currency='EUR')
        self.assertRaises(ValidationError, price.full_clean)
    
    def test_amount_values_positive(self):
        try:
            price = Price(amount=20, product_id=1, unit=1, currency='EUR')
            price.full_clean()
        except ValidationError, e:
            self.fail(e)
    

class StandardPriceTest(TestCase):
    fixtures = ['patron', 'address', 'category', 'price', 'product']
    
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
    fixtures = ['patron', 'address', 'category', 'price', 'product', 'booking']
    
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
    
