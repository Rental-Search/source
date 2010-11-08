# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase


class BookingTest(TestCase):
    fixtures = ['patron', 'address', 'price', 'product', 'booking', 'sinister']
    
    def test_preapproval_success(self):
        response = self.client.get(reverse('booking_success', args=['8fd2f3df67e2488496899aeb22601b15']))
        self.assertEquals(response.status_code, 200)
    
    def test_preapproval_failure(self):
        response = self.client.get(reverse('booking_failure', args=['8fd2f3df67e2488496899aeb22601b15']))
        self.assertEquals(response.status_code, 200)
    
