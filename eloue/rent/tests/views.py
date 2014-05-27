# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, timedelta, time
from decimal import Decimal as D
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.test import TransactionTestCase

from django.utils.translation import ugettext as _

from rent.models import Booking

from eloue.utils import currency, json

class BookingViewsTest(TransactionTestCase):
    reset_sequences = True
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
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '1']), {
            '0-started_at_0': started_at.strftime("%d/%m/%Y"),
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('duration' in json_res)
        self.assertTrue('total_price' in json_res)
        self.assertEquals(json_res['total_price'], json.loads(json.dumps(smart_str(currency(D('72.00'))))))
        self.assertEquals(json_res['duration'], '3 '+ "jours")
    
    def test_booking_price_error(self):
        started_at = self._next_weekday(0)
        ended_at = started_at - timedelta(days=3)
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '1']), {
            '0-started_at_0': started_at.strftime("%d/%m/%Y"),
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('errors' in json_res)
    
    def test_available_quantity_warning(self):
        started_at = self._next_weekday(0)
        ended_at = started_at + timedelta(days=3)
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '1']), {
            '0-started_at_0': started_at.strftime("%d/%m/%Y"),
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
            '0-ended_at_1': '08:00:00',
            '0-quantity': 2
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('warnings' in json_res)
    
    def test_booking_price_not_ajax(self):
        started_at = self._next_weekday(0)
        ended_at = started_at + timedelta(days=3)
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '1']), {
            '0-started_at_0': started_at.strftime("%d/%m/%Y"),
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1
        })
        self.assertEquals(response.status_code, 405)

class BookingViewsTestWithMultipleQuantity(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking', 'sinister']
    def setUp(self):
        
        self.now = datetime.combine((datetime.now() + timedelta(days=2)).date(), time(8, 0, 0))

        Booking.objects.create(
          started_at=self.now+timedelta(days=1),
          ended_at=self.now+timedelta(days=2),
          quantity=2,
          total_amount=7,
          state=Booking.STATE.ONGOING,
          owner_id=1,
          borrower_id=2,
          product_id=7,
          contract_id=14
        )
        Booking.objects.create(
          started_at=self.now+timedelta(days=1, seconds=12*3600),
          ended_at=self.now+timedelta(days=3),
          quantity=1,
          total_amount=D(str(7*1.5)),
          state=Booking.STATE.ONGOING,
          owner_id=1,
          borrower_id=2,
          product_id=7,
          contract_id=15
        )
    
    def test_all_available(self):
        started_at = self.now
        ended_at = self.now + timedelta(days=1)
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '7']) , {
          '0-started_at_0': started_at.strftime("%d/%m/%Y"),
          '0-started_at_1': "08:00:00",
          '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
          '0-ended_at_1': ended_at.strftime("%H:%M:%S"),
          '0-quantity': 3
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('max_available' in json_res)
        self.assertEqual(json_res['max_available'], 3)
        self.assertFalse('warnings' in json_res)
        self.assertFalse('errors' in json_res)

    def test_some_available(self):
        started_at = self.now
        ended_at = self.now + timedelta(days=1, seconds=12*3600)
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '7']) , {
          '0-started_at_0': started_at.strftime("%d/%m/%Y"),
          '0-started_at_1': started_at.strftime("%H:%M:%S"),
          '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
          '0-ended_at_1': ended_at.strftime("%H:%M:%S"),
          '0-quantity': 3
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('warnings' in json_res)
        self.assertFalse('errors' in json_res)
        self.assertTrue('max_available' in json_res)
        self.assertEqual(json_res['max_available'], 1)
    
    def test_enough_available(self):
        started_at = self.now + timedelta(days=1)
        ended_at = self.now + timedelta(days=1, seconds=12*3600)
        response = self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '7']) , {
          '0-started_at_0': started_at.strftime("%d/%m/%Y"),
          '0-started_at_1': started_at.strftime("%H:%M:%S"),
          '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
          '0-ended_at_1': ended_at.strftime("%H:%M:%S"),
          '0-quantity': 1
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('max_available' in json_res)
        self.assertEqual(json_res['max_available'], 1)
        self.assertFalse('warnings' in json_res)
        self.assertFalse('errors' in json_res)


    def test_none_available(self):
        started_at = self.now + timedelta(days=1, seconds=6*3600)
        ended_at = self.now + timedelta(days=2)
        response =  self.client.get(reverse('booking_price', args=['rent/bebe/mobilier-bebe/lits/', 'perceuse-visseuse-philips', '7']) , {
          '0-started_at_0': started_at.strftime("%d/%m/%Y"),
          '0-started_at_1': started_at.strftime("%H:%M:%S"),
          '0-ended_at_0': ended_at.strftime("%d/%m/%Y"),
          '0-ended_at_1': ended_at.strftime("%H:%M:%S"),
          '0-quantity': 1
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertTrue('max_available' in json_res)
        self.assertEqual(json_res['max_available'], 0)
        self.assertFalse('warnings' in json_res)
        self.assertTrue('errors' in json_res)
