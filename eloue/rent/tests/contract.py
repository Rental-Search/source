# -*- coding: utf-8 -*-
from pyPdf import PdfFileReader

from django.test import TestCase
from django.utils.translation import ugettext as _

from eloue.rent.contract import ContractGeneratorNormal
from eloue.rent.models import Booking


class ContractTest(TestCase):
    fixtures = ['category', 'patron', 'phones', 'address', 'price', 'product', 'booking']
    
    def test_standard_contract_generator(self):
        booking = Booking.objects.all()[0]
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        self.assertEquals(reader.getNumPages(), 1)
    
    def test_first_page(self):
        booking = Booking.objects.all()[0]
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        text = reader.getPage(0).extractText()
        self.assertTrue(booking.owner.get_full_name() in text)
        self.assertTrue(booking.borrower.get_full_name() in text)
        self.assertTrue(booking.borrower.get_full_name() in text)
    
    def test_second_page(self):
        booking = Booking.objects.all()[0]
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        text = reader.getPage(0).extractText()
        self.assertTrue(booking.product.summary in text)
        self.assertTrue("%s %s." % (booking.total_amount, booking.currency) in text)
    
    def test_third_page(self):
        booking = Booking.objects.all()[0]
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        text = reader.getPage(0).extractText()
        self.assertTrue("%s %s / %s %ss" % (booking.deposit_amount, booking.currency, _("dix"), _("euro")) in text)
    
    def test_zero_deposit_amount(self):
        booking = Booking.objects.all()[0]
        booking.deposit_amount = 0
        booking.save()
        generator = ContractGeneratorNormal()
        contract = generator(booking)
        reader = PdfFileReader(contract)
        self.assertEquals(reader.getNumPages(), 1)
    
