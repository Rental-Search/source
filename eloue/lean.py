# -*- coding: utf-8 -*-
from django.db.models import Q

from eloue.rent.models import Booking

class PatronEngagementScoreCalculator(object):
    def calculate_user_engagement_score(self, patron, start_date, end_date):
        """Calculate engagement as commission we made from this user booking"""
        days_in_period = (end_date - start_date).days + 1
        period_fee_total = sum([booking.commission for booking in Booking.objects.filter(created_at__gte=start_date, created_at__lte=end_date).filter(Q(owner=patron) | Q(borrower=patron))])
        return ((float)(period_fee_total) / days_in_period)
    
