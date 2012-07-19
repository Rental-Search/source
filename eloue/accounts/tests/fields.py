# -*- coding: utf-8 -*-

from django.test import TestCase

from django import forms
from eloue.accounts.fields import (RIBField, RIBWidget, HiddenRIBWidget, 
    ExpirationWidget, HiddenExpirationWidget, ExpirationField)


class RIBWidgetTest(TestCase):
    def testRIBWidget(self):
        widget = RIBWidget()
        self.assertEqual(
            widget.decompress('30004 00823 00001062805 03'),
            widget.decompress('30004008230000106280503')
        )
        self.assertEqual(
            widget.decompress('20041 01005 0500013M026 06'),
            widget.decompress('20041010050500013M02606')
        )
        self.assertEqual(
            widget.decompress('30004 00823 00001062805 03'),
            ('30004', '00823', '00001062805', '03')
        )
        self.assertEqual(
            widget.decompress('20041 01005 0500013M026 06'),
            ('20041', '01005', '0500013M026', '06')
        )
        self.assertEqual(
            widget.decompress(''),
            (None, None, None, None)
        )

        widget = HiddenRIBWidget()
        self.assertEqual(
            widget.decompress('30004 00823 00001062805 03'),
            widget.decompress('30004008230000106280503')
        )
        self.assertEqual(
            widget.decompress('20041 01005 0500013M026 06'),
            widget.decompress('20041010050500013M02606')
        )
        self.assertEqual(
            widget.decompress('30004 00823 00001062805 03'),
            ('30004', '00823', '00001062805', '03')
        )
        self.assertEqual(
            widget.decompress('20041 01005 0500013M026 06'),
            ('20041', '01005', '0500013M026', '06')
        )
        self.assertEqual(
            widget.decompress(''),
            (None, None, None, None)
        )


class RIBFieldTest(TestCase):

    def testRibFieldInvalid(self):
        field = RIBField()
        self.assertRaises(forms.ValidationError, field.clean, [])
        self.assertRaises(forms.ValidationError, field.clean, ['', '', '', ''])
        self.assertRaises(forms.ValidationError, field.clean, ['2345', '', '', ''])
        self.assertRaises(forms.ValidationError, field.clean, ['2345', '', ])
        self.assertRaises(forms.ValidationError, field.clean, ['30004', '00823', '00001062805', '04'])

    def testRIBFieldValid(self):
        field = RIBField()
        self.assertTrue(field.clean(['30004', '00823', '00001062805', '03']))
        self.assertTrue(field.clean(['20041', '01005', '0500013M026', '06']))


class ExpirationWidgetTest(TestCase):
    def testExpirationWidget(self):
        widget = ExpirationWidget()
        self.assertEqual(widget.decompress('0110'), ('01', '10'))
        widget = HiddenExpirationWidget()
        self.assertEqual(widget.decompress('0110'), ('01', '10'))


class ExpirationFieldTest(TestCase):
    def testExpirationFieldValid(self):
        field = ExpirationField()
        self.assertTrue(field.clean(['01', '12']))
        self.assertTrue(field.clean(['12', '22']))

    def testExpirationFieldInvalid(self):
        field = ExpirationField()
        self.assertRaises(forms.ValidationError, field.clean, [])
        self.assertRaises(forms.ValidationError, field.clean, ['','14'])
        self.assertRaises(forms.ValidationError, field.clean, ['14', ''])
        self.assertRaises(forms.ValidationError, field.clean, ['00', '12'])
        self.assertRaises(forms.ValidationError, field.clean, ['13', '12'])
        self.assertRaises(forms.ValidationError, field.clean, ['13', '11'])
        self.assertRaises(forms.ValidationError, field.clean, ['13', '23'])

