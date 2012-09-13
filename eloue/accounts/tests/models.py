# -*- coding: utf-8 -*-
import datetime
import unittest2
import mock

from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.contrib.auth.models import User

from eloue.accounts.models import Patron, Address, CreditCard, ProPackage
from eloue.payments.paybox_payment import PayboxManager
from eloue.wizard import MultiPartFormWizard

class CreditCardTest(TestCase):
    fixtures = ['patron']

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    @mock.patch.object(PayboxManager, 'unsubscribe')
    def test_delete(self, unsubscribe_mock):
        unsubscribe_mock.return_value = None
        cc = CreditCard(card_number='123123', expires='0319', holder=Patron.objects.get(pk=1))
        cc.save()
        cc.delete()
        self.assertTrue(unsubscribe_mock.called)
        unsubscribe_mock.called_with(1)

class AccountManagerTest(TestCase):
    def test_inactive_account_creation(self):
        patron = Patron.objects.create_inactive('benoit', 'benoit.woj@e-loue.com', 'benoit')
        self.assertEquals(patron.username, 'benoit')
        self.assertEquals(patron.email, 'benoit.woj@e-loue.com')
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue('benoit.woj@e-loue.com' in mail.outbox[0].to)
    
    def test_activate_account(self):
        patron = Patron.objects.create_inactive('benoit', 'benoit.woj@e-loue.com', 'benoit')
        self.assertEquals(patron.is_active, False)
        self.assertTrue(patron.activation_key != None)
        self.assertTrue(Patron.objects.activate(patron.activation_key))
        self.assertFalse(patron.is_expired())
        patron = Patron.objects.get(pk=patron.pk)
        self.assertTrue(patron.is_active)
        self.assertEquals(patron.activation_key, None)
    
    def test_activate_with_wrong_key(self):
        self.assertFalse(Patron.objects.activate('this is not a valid key'))
        self.assertFalse(Patron.objects.activate('36e6668dc35211df14deb911b4cb29f4577d0733'))
    
    @unittest2.skip
    def test_activate_with_expired_account(self):
        patron = Patron.objects.create_inactive('benoitw', 'benoit.woj@e-loue.com', 'benoit')
        self.assertEquals(patron.is_active, False)
        self.assertTrue(patron.activation_key != None)
        self.assertTrue(Patron.objects.activate(patron.activation_key))
        patron.date_joined = datetime.datetime.now() - datetime.timedelta(days=8)
        patron.save()
        self.assertTrue(patron.is_expired())
        self.assertFalse(Patron.objects.activate(patron.activation_key))
    
    def test_patron_exists(self):
        patron = Patron.objects.create_user('benoitw', 'benoit.woj@e-loue.com', 'benoit')
        self.assertTrue(Patron.objects.exists(pk=patron.pk))
        patron.delete()
        self.assertFalse(Patron.objects.exists(pk=patron.pk))
      
        
    def test_delete_expired(self):
        patron = Patron.objects.create_inactive('benoitw', 'benoit.woj@e-loue.com', 'benoit')
        patron.date_joined = datetime.datetime.now() - datetime.timedelta(days=8)
        patron.save()
        Patron.objects.delete_expired()
        self.assertRaises(Patron.DoesNotExist, Patron.objects.get, pk=patron.pk)
    
    def test_email_uniqueness(self):
        Patron.objects.create_user('benoitc', 'benoit.woj@e-loue.com', 'benoit')
        patron = Patron(username='benoitw', email='benoit.woj@e-loue.com', password="!")
        self.assertRaises(ValidationError, patron.full_clean)
    
    def test_email_existing_uniqueness(self):
        try:
            patron = Patron.objects.create_user('benoitc', 'benoit.woj@e-loue.com', 'benoit')
            patron.full_clean()
        except ValidationError, e:
            self.fail(e)
    

class AccountTest(TestCase):
    def test_modified_at(self):
        patron = Patron.objects.create_user('benoit', 'benoit@e-loue.com', 'benoit')
        self.assertTrue(patron.modified_at <= datetime.datetime.now())
        modified_at = patron.modified_at
        patron.save()
        self.assertTrue(modified_at <= patron.modified_at <= datetime.datetime.now())
    

class AddressTest(TestCase):
    fixtures = ['patron']
    
    def test_latitude_too_high(self):
        address = Address(position=Point(270, 40),
            address1='11, rue debelleyme',
            patron_id=1,
            country='FR',
            city='Paris',
            zipcode='75003'
        )
        self.assertRaises(ValidationError, address.full_clean)
    
    def test_latitude_too_low(self):
        address = Address(position=Point(-270, 40),
            address1='11, rue debelleyme',
            patron_id=1,
            country='FR',
            city='Paris',
            zipcode='75003'
        )
        self.assertRaises(ValidationError, address.full_clean)
    
    def test_longitude_too_high(self):
        address = Address(position=Point(40, 270),
            address1='11, rue debelleyme',
            patron_id=1,
            country='FR',
            city='Paris',
            zipcode='75003'
        )
        self.assertRaises(ValidationError, address.full_clean)
    
    def test_longitude_too_low(self):
        address = Address(position=Point(40, -270),
            address1='11, rue debelleyme',
            patron_id=1,
            country='FR',
            city='Paris',
            zipcode='75003'
        )
        self.assertRaises(ValidationError, address.full_clean)
    
    def test_correct_coordinates(self):
        try:
            address = Address(position=Point(48.8613232, 2.3631101),
                address1='11, rue debelleyme',
                patron_id=1,
                country='FR',
                city='Paris',
                zipcode='75003'
            )
            address.full_clean()
        except ValidationError, e:
            self.fail(e)

class BillingTest(TestCase):
    
    def setUp(self):
        patron = Patron.objects.get(pk=7)

    def test_subscribed(self):
        patron = Patron.objects.get(pk=7)
        self.assertTrue(patron.current_subscription)
        self.assertTrue(patron.is_professional)

    def test_not_subscribed(self):
        patron = Patron.objects.get(pk=6)
        self.assertFalse(patron.current_subscription)
        self.assertFalse(patron.is_professional)

    def test_subscription_price(self):
        patron = Patron.objects.get(pk=7)
        subscription = patron.current_subscription
        package = subscription.propackage
        first_of_february = datetime.datetime(2012, 2, 1)
        first_of_march = datetime.datetime(2012, 3, 1)
        first_of_april = datetime.datetime(2012, 4, 1)
        first_of_may = datetime.datetime(2012, 5, 1)
        self.assertEqual(subscription.price(first_of_february, first_of_march), package.price)
        self.assertEqual(subscription.price(first_of_march, first_of_april), package.price)
        self.assertEqual(subscription.price(first_of_april, first_of_may), package.price)

    @mock.patch.object(MultiPartFormWizard, 'security_hash')
    def test_subscription_product_add(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        patron = Patron.objects.get(pk=7)
        self.client.login(username='elouetest1@gmail.com', password=' ')
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            '1-addresses__address1': 'wiefoij',
            '1-addresses__zipcode': '23432',
            '1-addresses__city': 'woe',
            '1-addresses__country': 'FR',
            '1-phones__phone': '23425232', 
            'wizard_step': 1,
            'hash_1': '6941fd7b20d720833717a1f92e8027af'
        })
        # print response.context['form'].errors
        self.assertRedirects(response, 'location/bebe/mobilier-bebe/lits/bentley-brooklands-1/')
