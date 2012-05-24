# -*- coding: utf-8 -*-
import mock

from django.test import TestCase

from eloue.accounts.forms import (RIBForm, CreditCardForm, mask_card_number, 
    CvvForm, EmailAuthenticationForm)
from eloue.accounts.models import Patron
from eloue.payments.paybox_payment import PayboxManager, PayboxException

class RIBFormTest(TestCase):
    def testValidRib(self):
        form = RIBForm(
            {
                'rib_0': '30004', 'rib_1': '00823',
                'rib_2': '00001062805', 'rib_3': '03'
            }
        )
        self.assertTrue(form.is_valid())
        form = RIBForm(
            {
                'rib_0': '20041', 'rib_1': '01005',
                'rib_2': '0500013M026', 'rib_3': '06'
            }
        )
        self.assertTrue(form.is_valid())

    def testInvalidRib(self):
        form = RIBForm(
            {
                'rib_0': '20041', 'rib_1': '01005',
                'rib_2': '0500013M026', 'rib_3': '07'
            }
        )
        self.assertFalse(form.is_valid())
        form = RIBForm(
            {
                'rib_0': '30004', 'rib_1': '00823',
                'rib_2': '00001062805', 'rib_3': '04'
            }
        )
        self.assertFalse(form.is_valid())


class CreditCardFormTest(TestCase):
    fixtures = ['patron']

    @mock.patch.object(PayboxManager, 'authorize')
    def testEmptyFail(self, mock_authorize):
        form = CreditCardForm({})
        self.assertFalse(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertTrue(form.errors)
        self.assertTrue('cvv' in form.errors)
        self.assertTrue('expires' in form.errors)
        self.assertTrue('card_number' in form.errors)
        self.assertFalse(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize')
    def testLuhnFail(self, mock_authorize):
        self.assertFalse(
            CreditCardForm(
                {
                    'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                    'card_number': '1111222233334445',  'holder_name': 'xxx'
                }
            ).is_valid()
        )
        self.assertFalse(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize')
    def testCardWithLetters(self, mock_authorize):
        form = CreditCardForm({
                'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                'card_number': '111122222aaaa4444',  'holder_name': 'xxx'
            })
        self.assertFalse(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertTrue(form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('card_number' in form.errors)

    @mock.patch.object(PayboxManager, 'authorize')
    def testCardWithoutHolderName(self, mock_authorize):
        form = CreditCardForm({
                'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                'card_number': '1111222233334444', 'holder_name': ''
            })
        self.assertFalse(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertTrue(form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('holder_name' in form.errors)

    @mock.patch.object(PayboxManager, 'authorize')
    def testExpiredFail(self, mock_authorize):
        mock_authorize.side_effect = PayboxException(11, '')
        form = CreditCardForm(
            {
                'cvv': '123', 'expires_0': '02', 'expires_1': '12',
                'card_number': '1111222233334444',  'holder_name': 'xxx'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.non_field_errors())
        self.assertEqual(form.non_field_errors(), form.errors['__all__'])
        self.assertTrue(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize')
    def testExpiredValid(self, mock_authorize):
        mock_authorize.return_value = ('0001234', '000012345')
        form = CreditCardForm(
            {
                'cvv': '123', 'expires_0': '02', 'expires_1': '22',
                'card_number': '1111222233334444',  'holder_name': 'xxx'
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(mock_authorize.called)
        self.assertFalse(form.errors)
        self.assertFalse(form.non_field_errors())

    @mock.patch.object(PayboxManager, 'subscribe')
    @mock.patch.object(PayboxManager, 'modify')
    @mock.patch.object(PayboxManager, 'authorize')
    def testSave(self, mock_authorize, mock_modify, mock_subscribe):
        mock_authorize.return_value = ('0001234', '000012345')
        form = CreditCardForm({
                'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                'card_number': '1111222233334444',  'holder_name': 'xxx',
            }, instance=CreditCardForm._meta.model(holder=Patron.objects.get(pk=1)))
        self.assertTrue(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertFalse(form.errors)
        self.assertTrue(isinstance(form.save(commit=False), CreditCardForm._meta.model))
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        self.assertFalse(mock_modify.called)

    def testCardNumberMask(self):
        self.assertEquals(mask_card_number('1111222233334444'), '1XXXXXXXXXXXX444')

    @mock.patch.object(PayboxManager, 'subscribe')
    @mock.patch.object(PayboxManager, 'modify')
    @mock.patch.object(PayboxManager, 'authorize')
    def testSaveCommitNew(self, mock_authorize, mock_modify, mock_subscribe):
        mock_authorize.return_value = ('0001234', '000012345')
        mock_subscribe.return_value = 'SLDLrcsLMPC'
        form = CreditCardForm({
                'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                'card_number': '1111222233334444',  'holder_name': 'xxx'
            }, instance=CreditCardForm._meta.model(holder=Patron.objects.get(pk=1)))
        self.assertTrue(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertFalse(form.errors)
        self.assertTrue(isinstance(form.save(commit=True), CreditCardForm._meta.model))
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        self.assertFalse(mock_modify.called)

    @mock.patch.object(PayboxManager, 'subscribe')
    @mock.patch.object(PayboxManager, 'modify')
    @mock.patch.object(PayboxManager, 'authorize')
    def testSaveCommitExisting(self, mock_authorize, mock_modify, mock_subscribe):
        mock_authorize.return_value = ('0001234', '000012345')
        mock_modify.return_value = 'SLDLrcsLMPC'
        form = CreditCardForm({
                'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                'card_number': '1111222233334444', 'holder_name': 'xxx'
            }, instance=CreditCardForm._meta.model(
                holder=Patron.objects.get(pk=1), card_number='SLDLrcsLMPC', pk=1,
                expires='1222', masked_number='1XXXXXXXXXXXX444', holder_name='xxx'
            )
        )
        self.assertTrue(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertFalse(form.errors)
        self.assertTrue(isinstance(form.save(commit=True), CreditCardForm._meta.model))
        self.assertTrue(mock_authorize.called)
        self.assertFalse(mock_subscribe.called)
        self.assertTrue(mock_modify.called)


    @mock.patch.object(PayboxManager, 'subscribe')
    @mock.patch.object(PayboxManager, 'modify')
    @mock.patch.object(PayboxManager, 'authorize')
    def testSaveCommitFail(self, mock_authorize, mock_modify, mock_subscribe):
        mock_authorize.return_value = ('0001234', '000012345')
        mock_subscribe.side_effect = PayboxException(16, 'Abonne deja existant')
        form = CreditCardForm({
                'cvv': '123', 'expires_0': '12', 'expires_1': '22',
                'card_number': '1111222233334444',  'holder_name': 'xxx'
            }, instance=CreditCardForm._meta.model(holder=Patron.objects.get(pk=1)))
        self.assertTrue(form.is_valid())
        self.assertFalse(form.non_field_errors())
        self.assertFalse(form.errors)
        self.assertRaises(PayboxException, form.save, commit=True)
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        self.assertFalse(mock_modify.called)

class CvvFormTest(TestCase):
    fixtures = ['patron']

    def testWithoutInstance(self):
        self.assertRaises(ValueError, CvvForm, {})

    @mock.patch.object(PayboxManager, 'authorize_subscribed')
    def testEmptyFail(self, mock_authorize):
        form = CvvForm({'cvv': ''}, instance=CreditCardForm._meta.model(
                holder=Patron.objects.get(pk=1), card_number='SLDLrcsLMPC',
                expires='1222', masked_number='1XXXXXXXXXXXX444'
            ))
        self.assertFalse(form.is_valid())
        self.assertTrue('cvv' in form.errors)
        self.assertFalse(form.non_field_errors())
        self.assertFalse(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize_subscribed')
    def testTooShortFail(self, mock_authorize):
        form = CvvForm({'cvv': '11'}, instance=CreditCardForm._meta.model(
                holder=Patron.objects.get(pk=1), card_number='SLDLrcsLMPC',
                expires='1222', masked_number='1XXXXXXXXXXXX444'
            ))
        self.assertFalse(form.is_valid())
        self.assertTrue('cvv' in form.errors)
        self.assertFalse(form.non_field_errors())
        self.assertFalse(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize_subscribed')
    def testTooLongFail(self, mock_authorize):
        form = CvvForm({'cvv': '11111'}, instance=CreditCardForm._meta.model(
                holder=Patron.objects.get(pk=1), card_number='SLDLrcsLMPC',
                expires='1222', masked_number='1XXXXXXXXXXXX444'
            ))
        self.assertFalse(form.is_valid())
        self.assertTrue('cvv' in form.errors)
        self.assertFalse(form.non_field_errors())
        self.assertFalse(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize_subscribed')
    def testValidationError(self, mock_authorize):
        mock_authorize.side_effect = PayboxException(19, 'Wrong card data')
        form = CvvForm({'cvv': '1111'}, instance=CreditCardForm._meta.model(
                holder=Patron.objects.get(pk=1), card_number='SLDLrcsLMPC',
                expires='1222', masked_number='1XXXXXXXXXXXX444'
            ))
        self.assertFalse(form.is_valid())
        self.assertFalse('cvv' in form.errors)
        self.assertTrue(form.non_field_errors())
        self.assertTrue(mock_authorize.called)

    @mock.patch.object(PayboxManager, 'authorize_subscribed')
    def testValid(self, mock_authorize):
        mock_authorize.return_value = ('0001234', '0001234')
        form = CvvForm({'cvv': '1111'}, instance=CreditCardForm._meta.model(
                holder=Patron.objects.get(pk=1), card_number='SLDLrcsLMPC',
                expires='1222', masked_number='1XXXXXXXXXXXX444'
            ))
        self.assertTrue(form.is_valid())
        self.assertFalse('cvv' in form.errors)
        self.assertFalse(form.non_field_errors())
        self.assertTrue(mock_authorize.called)
        self.assertRaises(NotImplementedError, form.save, commit=True)
        self.assertTrue(isinstance(form.save(commit=False), CreditCardForm._meta.model))

