# -*- coding: utf-8 -*-
from django.test import TestCase

from eloue.rent.contract import ContractGenerator
from eloue.rent.models import Booking

class ContractTest(TestCase):
    fixtures = ['patron', 'phones', 'address', 'price', 'product', 'booking']
    
    def test_standard_contract_generator(self):
        booking = Booking.objects.all()[0]
        generator = ContractGenerator()
        fd = generator(booking)
    
