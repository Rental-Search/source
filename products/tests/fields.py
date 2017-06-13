from django.test import TestCase
from django.forms import ValidationError

from products.fields import FRLicensePlateField

class LicensePlateTest(TestCase):

	def testEmptyPlate(self):
		self.assertEqual(FRLicensePlateField(required=False).clean(''), '')
		self.assertRaises(ValidationError, FRLicensePlateField(required=True).clean, '')

	def testValidNewPlate(self):
		field = FRLicensePlateField()
		self.assertEqual(field.clean('AA-229-AA'), 'AA-229-AA')
		self.assertEqual(field.clean('AA-\+229 aa'), 'AA-229-AA')
		self.assertEqual(field.clean('Aa 229 bb'), 'AA-229-BB')
		self.assertEqual(field.clean('Aa 229 WW'), 'AA-229-WW')


	def testValidOldPlate(self):
		field = FRLicensePlateField()
		self.assertEqual(field.clean('1 A 00'), '1 A 00')
		self.assertEqual(field.clean('999 Z 00'), '999 Z 00')
		self.assertEqual(field.clean('1=-)AA 00'), '1 AA 00')
		self.assertEqual(field.clean('999 PZ00'), '999 PZ 00')
		self.assertEqual(field.clean('1 QA00'), '1 QA 00')
		self.assertEqual(field.clean('9999ZZ 00'), '9999 ZZ 00')
		self.assertEqual(field.clean('11-()AAA 00'), '11 AAA 00')
		self.assertEqual(field.clean('999 ZZZ 00'), '999 ZZZ 00')

	def testInvalidPlate(self):
		field = FRLicensePlateField()
		self.assertRaises(ValidationError, field.clean, '12,34, 44')
		self.assertRaises(ValidationError, field.clean, 'SS 432-QQ')
		self.assertRaises(ValidationError, field.clean, 'WW 432-SS')