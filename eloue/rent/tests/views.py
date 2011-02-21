# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson


class BookingViewsTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking', 'sinister']
    
    def _next_weekday(self, weekday):
        """Get next weekday as a datetime"""
        day = datetime.now() + timedelta(days=1)
        while calendar.weekday(*day.timetuple()[:3]) != weekday:
            day = day + timedelta(days=1)
        return day
    
    def test_preapproval_success(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('booking_success', args=['8fd2f3df67e2488496899aeb22601b15']))
        self.assertEquals(response.status_code, 200)
    
    def test_preapproval_failure(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('booking_failure', args=['8fd2f3df67e2488496899aeb22601b15']))
        self.assertEquals(response.status_code, 200)
    
    def test_booking_price(self):
        started_at = self._next_weekday(0)
        ended_at = started_at + timedelta(days=3)
        response = self.client.get(reverse('booking_price', args=['perceuse-visseuse-philips', '1']), {
            '0-started_at_0': started_at.strftime("%d/%m/%Y"),
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
            '0-ended_at_1': '08:00:00'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertTrue('duration' in json)
        self.assertTrue('total_price' in json)
        self.assertEquals(json['total_price'], '28.00')
        self.assertEquals(json['duration'], '4 days')
    
