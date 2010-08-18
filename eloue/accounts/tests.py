# -*- coding: utf-8 -*-
import datetime

from django.core import mail
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from eloue.accounts.models import Patron

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
        self.assertEquals(patron.activation_key, "ALREADY_ACTIVATED")
    
    def test_activate_with_wrong_key(self):
        self.assertFalse(Patron.objects.activate('this is not a valid key'))
        self.assertFalse(Patron.objects.activate('36e6668dc35211df14deb911b4cb29f4577d0733'))
    
    def test_activate_with_expired_account(self):
        patron = Patron.objects.create_inactive('benoitc', 'benoitc.woj@e-loue.com', 'benoit')
        self.assertEquals(patron.is_active, False)
        self.assertTrue(patron.activation_key != None)
        self.assertTrue(Patron.objects.activate(patron.activation_key))
        patron.date_joined = datetime.datetime.now() - datetime.timedelta(days=8)
        patron.save()
        self.assertTrue(patron.is_expired())
        self.assertFalse(Patron.objects.activate(patron.activation_key))
    
    def test_patron_exists(self):
        patron = Patron.objects.create_user('benoitc', 'benoitc.woj@e-loue.com', 'benoit')
        self.assertTrue(Patron.objects.exists(pk=patron.pk))
        patron.delete()
        self.assertFalse(Patron.objects.exists(pk=patron.pk))
    
    def test_delete_expired(self):
        patron = Patron.objects.create_inactive('benoitc', 'benoitc.woj@e-loue.com', 'benoit')
        patron.date_joined = datetime.datetime.now() - datetime.timedelta(days=8)
        patron.save()
        Patron.objects.delete_expired()
        self.assertRaises(Patron.DoesNotExist, Patron.objects.get, pk=patron.pk)
    

class AccountTest(TestCase):
    def test_modified_at(self):
        patron = Patron.objects.create_user('benoit', 'benoit@e-loue.com', 'benoit')
        patron.save()
        self.assertTrue(patron.modified_at <= datetime.datetime.now())
        modified_at = patron.modified_at
        patron.save()
        self.assertTrue(modified_at <= patron.modified_at <= datetime.datetime.now())
    
