# -*- coding: utf-8 -*-
import datetime

from django.core import mail
from django.test import TestCase
from django.core.exceptions import ValidationError

from eloue.accounts.models import Patron, Comment

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
        except ValdiationError, e:
            self.fail(e)
    

class AccountTest(TestCase):
    def test_modified_at(self):
        patron = Patron.objects.create_user('benoit', 'benoit@e-loue.com', 'benoit')
        self.assertTrue(patron.modified_at <= datetime.datetime.now())
        modified_at = patron.modified_at
        patron.save()
        self.assertTrue(modified_at <= patron.modified_at <= datetime.datetime.now())
    

class CommentTest(TestCase):
    fixtures = ['patron']
    
    def test_created_at(self):
        comment = Comment.objects.create(score=1.0, patron_id=1)
        self.assertTrue(comment.created_at <= datetime.datetime.now())
        created_at = comment.created_at
        comment.save()
        self.assertEquals(comment.created_at, created_at)
    
    def test_score_values_negative(self):
        comment = Comment(score=-1.0, patron_id=1, description="Incorrect")
        self.assertRaises(ValidationError, comment.full_clean)
    
    def test_score_values_too_high(self):
        comment = Comment(score=2.0, patron_id=1, description="Trop parfait")
        self.assertRaises(ValidationError, comment.full_clean)
    
    def test_score_values_correct(self):
        try:
            comment = Comment(score=0.5, patron_id=1, description="Correct")
            comment.full_clean()
        except ValidationError, e:
            self.fail(e)
    
