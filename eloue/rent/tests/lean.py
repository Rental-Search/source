# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase

from eloue.accounts.models import Patron
from eloue.lean import PatronEngagementScoreCalculator


class ScoreCalculatorTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']
    
    def test_classic_period(self):
        score_calculator = PatronEngagementScoreCalculator()
        patron = Patron.objects.get(pk=1)
        score = score_calculator.calculate_user_engagement_score(
            patron, datetime(2010, 8, 14), datetime(2010, 8, 20)
        )
        self.assertAlmostEqual(3.4285714285714284, score)
    
