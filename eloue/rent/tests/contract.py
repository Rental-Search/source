# -*- coding: utf-8 -*-
from pyPdf import PdfFileReader

from django.test import TestCase
from django.utils.translation import ugettext as _

from eloue.rent.contract import ContractGeneratorNormal
from eloue.rent.models import Booking


class ContractTest(TestCase):
    fixtures = ['category', 'patron', 'phones', 'address', 'price', 'product', 'booking', 'creditcard', 'payments']
    
    def test_standard_contract_generator(self):
        booking = Booking.objects.get(pk='87ee8e9dec1d47c29ebb27e09bda8fc3')
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        self.assertEquals(reader.getNumPages(), 3)
    
    def test_second_page(self):
        booking = Booking.objects.get(pk='87ee8e9dec1d47c29ebb27e09bda8fc3')
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        text = reader.getPage(1).extractText()
        self.assertTrue(booking.product.summary in text)
        self.assertTrue("%s" % (booking.total_amount) in text)
    
    def test_zero_deposit_amount(self):
        booking = Booking.objects.get(pk='87ee8e9dec1d47c29ebb27e09bda8fc3')
        booking.deposit_amount = 0
        booking.save()
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        self.assertEquals(reader.getNumPages(), 3)
    
