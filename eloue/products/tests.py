# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.core.exceptions import ValidationError

from eloue.products.models import Review, Price, SeasonalPrice

class ReviewTest(TestCase):
    def test_score_values(self):
        review = Review(score=-1.0)
        self.assertRaises(ValidationError, review.full_clean)
        review = Review(score=2.0)
        self.assertRaises(ValidationError, review.full_clean)
        review = Review(score=0.5)
        self.failUnlessRaises(ValidationError, review.full_clean)
    

class PriceTest(TestCase):
    def test_amount_values(self):
        price = Price(amount=-1)
        self.assertRaises(ValidationError, price.full_clean)
        price = Price(amount=20)
        self.failUnlessRaises(ValidationError, price.full_clean)
    

class SeasonalTest(TestCase):
    def test_start_and_end_date(self):
        seasonal_price = SeasonalPrice(
            started_at=datetime.datetime.now() + datetime.timedelta(days=3),
            ended_at=datetime.datetime.now()
        )
        self.assertRaises(ValidationError, seasonal_price.full_clean)
    
