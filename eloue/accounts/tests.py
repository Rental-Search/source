# -*- coding: utf-8 -*-
import datetime

from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.test import TestCase

from eloue.accounts.models import Patron, Address

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
    

class PatronTest(TestCase):
    fixtures = ['patron']
    
    def test_patron_detail_view(self):
        response = self.client.get(reverse('patron_detail', args=['alexandre']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patron'].slug, 'alexandre')
    
    def test_patron_detail_compat(self):
        response = self.client.get(reverse('patron_detail_compat', args=['alexandre', 1]))
        self.assertRedirects(response, reverse('patron_detail', args=['alexandre']), status_code=301)
    
