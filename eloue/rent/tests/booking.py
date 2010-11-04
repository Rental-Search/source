# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from eloue.rent.models import Booking


class TestPreapproval(TestCase):
    fixtures = ['patron', 'address', 'price', 'product', 'booking', 'sinister']
    
    def test_preapproval_success(self):
        response = self.client.get(reverse('booking_success', args=['8fd2f3df67e2488496899aeb22601b15']))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue('timothee.peignier@e-loue.com' in mail.outbox[0].to)
        booking = Booking.objects.get(pk='8fd2f3df67e2488496899aeb22601b15')
        self.assertEqual(booking.payment_state, Booking.PAYMENT_STATE.AUTHORIZED)
    
    def test_preapproval_failure(self):
        response = self.client.get(reverse('booking_failure', args=['8fd2f3df67e2488496899aeb22601b15']))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 0)
        booking = Booking.objects.get(pk='8fd2f3df67e2488496899aeb22601b15')
        self.assertEqual(booking.payment_state, Booking.PAYMENT_STATE.CANCELED)
    
