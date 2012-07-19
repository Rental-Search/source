# -*- coding: utf-8 -*-
import os

from django.core.urlresolvers import reverse
from django.test import TestCase

from mock import patch
from facebook import GraphAPIError, GraphAPI

from eloue.products.models import Picture
from eloue.wizard import MultiPartFormWizard
from eloue.products.models import Product, ProductRelatedMessage, MessageThread
from eloue.accounts.models import Address, FacebookSession, Patron
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

class ProductWizardTestWithFacebookAccount(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'picture', 'facebooksession']
    # with already existing account associated with a facebook session

    me1 = {
        u'email': u'balazs.kossovics@e-loue.com',
        u'first_name': u'Jacques-Yves',
        u'gender': u'male',
        u'id': u'100003207275288',
        u'last_name': u'Cousteau',
        u'link': u'http://www.facebook.com/profile.php?id=100003207275288',
        u'locale': u'en_GB',
        u'name': u'Jacques-Yves Cousteau',
        u'timezone': 1,
        u'updated_time': u'2011-11-23T09:25:40+0000'
    }

    me2 = {u'email': u'kosii.spam@gmail.com',
        u'first_{name': u'Bal\xe1zs',
        u'gender': u'male',
        u'id': u'100000609837182',
        u'last_name': u'Kossovics',
        u'link': u'http://www.facebook.com/kosii.spam',
        u'locale': u'en_US',
        u'name': u'Bal\xe1zs Kossovics',
        u'timezone': 1,
        u'updated_time': u'2011-11-23T16:42:03+0000',
        u'username': u'kosii.spam',
        u'verified': True
    }

    me3 = {u'email': u'elouetest@gmail.com',
        u'first_name': u'Noga',
        u'gender': u'male',
        u'id': u'100003190074813',
        u'last_name': u'Alon',
        u'link': u'http://www.facebook.com/profile.php?id=100003190074813',
        u'locale': u'en_US',
        u'name': u'Noga Alon',
        u'timezone': 1,
        u'updated_time': u'2011-11-25T16:14:45+0000'
    }

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_not_logged_in(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = ProductWizardTestWithFacebookAccount.me1

        uid = 100003207275288
        access_token = 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD'
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
        self.assertTrue(mock_object.called)
    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_not_logged_in(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = ProductWizardTestWithFacebookAccount.me1

        uid = 100003207275288
        access_token = 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD'
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            '2-addresses__address1': 'wiefoij',
            '2-addresses__zipcode': '23432',
            '2-addresses__city': 'woe',
            '2-addresses__country': 'FR',
            '2-phones__phone': '23425232', 
            'wizard_step': 2,
            'hash_1': '6941fd7b20d720833717a1f92e8027af'
        })
        self.assertRedirects(response, 'location/bebe/mobilier-bebe/lits/bentley-brooklands-8/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(mock_object.called)

    #as a new user logging in with facebook    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_new_user(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = ProductWizardTestWithFacebookAccount.me2

        uid = 100000609837182
        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        self.assertRaises(FacebookSession.DoesNotExist, FacebookSession.objects.get, uid=uid)
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
        FacebookSession.objects.get(uid=uid)
        self.assertTrue(mock_object.called)

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_new_user(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = ProductWizardTestWithFacebookAccount.me2

        uid = 100000609837182
        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        self.assertRaises(FacebookSession.DoesNotExist, FacebookSession.objects.get, uid=100000609837182)
        self.assertRaises(Patron.DoesNotExist, Patron.objects.get, username='kosii2')
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            '2-username': 'kosii2',
            '2-first_name': 'sdf',
            '2-last_name': 'gerg',
            '2-addresses__address1': 'wiefoij',
            '2-addresses__zipcode': '23432',
            '2-addresses__city': 'woe',
            '2-addresses__country': 'FR',
            '2-phones__phone': '23425232', 
            'wizard_step': 2,
            'hash_1': '6941fd7b20d720833717a1f92e8027af'
        })
        self.assertRedirects(response, 'location/bebe/mobilier-bebe/lits/bentley-brooklands-8/')
        self.assertTrue(response.status_code, 200)
        self.assertEqual(Patron.objects.get(username='kosii2'), FacebookSession.objects.get(uid=uid).user)
        self.assertTrue(mock_object.called)

    #as a new user logging in with facebook, but already started the registration procedure, so we have a FacesbookSession object
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_associate_accounts(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = ProductWizardTestWithFacebookAccount.me3

        uid = 100003190074813
        access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, None)
        Patron.objects.get(username='kosii1')
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, Patron.objects.get(username='kosii1'))
        self.assertTrue(mock_object.called)

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_associate_accounts(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = ProductWizardTestWithFacebookAccount.me3

        uid = 100003190074813
        access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, None)
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            '2-addresses__address1': 'wiefoij',
            '2-addresses__zipcode': '23432',
            '2-addresses__city': 'woe',
            '2-addresses__country': 'FR',
            '2-phones__phone': '23425232', 
            'wizard_step': 2,
            'hash_1': '6941fd7b20d720833717a1f92e8027af'
        })
        self.assertRedirects(response, 'location/bebe/mobilier-bebe/lits/bentley-brooklands-8/')
        self.assertTrue(response.status_code, 200)
        self.assertEqual(Patron.objects.get(username='kosii1'), FacebookSession.objects.get(uid=uid).user)
        self.assertTrue(mock_object.called)

class MessageWizardTestWithFacebook(TestCase):
    fixtures = ['category', 'patron', 'facebooksession', 'address', 'price', 'product', 'picture']

    me1 = {
        u'email': u'balazs.kossovics@e-loue.com',
        u'first_name': u'Jacques-Yves',
        u'gender': u'male',
        u'id': u'100003207275288',
        u'last_name': u'Cousteau',
        u'link': u'http://www.facebook.com/profile.php?id=100003207275288',
        u'locale': u'en_GB',
        u'name': u'Jacques-Yves Cousteau',
        u'timezone': 1,
        u'updated_time': u'2011-11-23T09:25:40+0000'
    }

    me2 = {u'email': u'kosii.spam@gmail.com',
        u'first_{name': u'Bal\xe1zs',
        u'gender': u'male',
        u'id': u'100000609837182',
        u'last_name': u'Kossovics',
        u'link': u'http://www.facebook.com/kosii.spam',
        u'locale': u'en_US',
        u'name': u'Bal\xe1zs Kossovics',
        u'timezone': 1,
        u'updated_time': u'2011-11-23T16:42:03+0000',
        u'username': u'kosii.spam',
        u'verified': True
    }

    me3 = {u'email': u'elouetest@gmail.com',
        u'first_name': u'Noga',
        u'gender': u'male',
        u'id': u'100003190074813',
        u'last_name': u'Alon',
        u'link': u'http://www.facebook.com/profile.php?id=100003190074813',
        u'locale': u'en_US',
        u'name': u'Noga Alon',
        u'timezone': 1,
        u'updated_time': u'2011-11-25T16:14:45+0000'
    }

    def setUp(self):
        self.product = Product.objects.get(pk=1)

    @patch.object(GraphAPI, 'get_object')
    def test_zero_step_logged_out(self, mock_object):
        mock_object.return_value = MessageWizardTestWithFacebook.me1

        access_token = "AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD"
        uid = 100003207275288
        response = self.client.post(reverse('message_create', kwargs={'product_id':self.product.pk, 'recipient_id': self.product.owner.pk}), {
            '0-subject':  'Hi',
            '0-body': 'How are you?',
            'wizard_step': 0
        })
        self.assertTemplateUsed(response, 'accounts/auth_login.html')
        self.assertFalse(mock_object.called)

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_first_step_logged_out(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'        
        mock_object.return_value = MessageWizardTestWithFacebook.me1

        access_token = "AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD"
        uid = 100003207275288
        response = self.client.post(reverse('message_create', kwargs={'product_id':self.product.pk, 'recipient_id': self.product.owner.pk}), {
            '0-subject':  'Hi',
            '0-body': 'How are you?',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'wizard_step': 1,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
        })
        self.assertRedirects(response, reverse('thread_details', kwargs={'thread_id': 1}))
    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_first_step_new_user(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = MessageWizardTestWithFacebook.me2

        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        uid = 100000609837182
        response = self.client.post(reverse('message_create', kwargs={'product_id':self.product.pk, 'recipient_id': self.product.owner.pk}), {
            '0-subject':  'Hi',
            '0-body': 'How are you?',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'wizard_step': 1,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
        })
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_new_user(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = MessageWizardTestWithFacebook.me2

        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        uid = 100000609837182
        response = self.client.post(reverse('message_create', kwargs={'product_id':self.product.pk, 'recipient_id': self.product.owner.pk}), {
            '0-subject':  'Hi',
            '0-body': 'How are you?',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'wizard_step': 2,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
        })
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_new_user(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = MessageWizardTestWithFacebook.me2

        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        uid = 100000609837182
        response = self.client.post(reverse('message_create', kwargs={'product_id':self.product.pk, 'recipient_id': self.product.owner.pk}), {
            '0-subject':  'Hi',
            '0-body': 'How are you?',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-username': 'kosii2',
            'wizard_step': 2,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_3': '6941fd7b20d720833717a1f92e8027af',
        })
        self.assertRedirects(response, reverse('thread_details', kwargs={'thread_id': 1}))
        self.assertEqual(FacebookSession.objects.get(uid=100000609837182).user, Patron.objects.get(username='kosii2'))

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_associate_user(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = MessageWizardTestWithFacebook.me3

        access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        uid = 100003190074813
        response = self.client.post(reverse('message_create', kwargs={'product_id':self.product.pk, 'recipient_id': self.product.owner.pk}), {
            '0-subject':  'Hi',
            '0-body': 'How are you?',
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            'wizard_step': 1,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af'
        })
        self.assertRedirects(response, reverse('thread_details', kwargs={'thread_id': 1}))

        
class ProductWizardTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'picture']
    
    def test_zero_step(self):
        response = self.client.get(reverse('product_create'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_create.html')
    
    def test_first_step_as_anonymous(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture': f,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            "0-payment_type":1,
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_login.html')
        self.assertEquals(Picture.objects.count(), 2)
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('product_create'), {
            '0-category': 1,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            "0-payment_type":1,
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        l = len(Product.objects.all())
        self.assertRedirects(response, reverse('booking_create', args=['bebe/mobilier-bebe/lits/', 'bentley-brooklands', l]))
        
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_first_step_message_wizard_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('message_create', args=[1, 1]), {
            '0-subject': 'Ask for price, test for wizard',
            '0-body': 'May I have a lower price? never send me a email',
            'wizard_step': 0
        })
        self.assertTemplateUsed(response, 'accounts/auth_login.html')

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_message_wizard_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('message_create', args=[6, 4]), {
            '0-subject': 'Ask for price, test for wizard',
            '0-body': 'May I have a lower price? never send me a email',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 301)
        product = Product.objects.get(pk=6)
        thread = MessageThread.objects.get(pk=1)
        self.assertEqual(thread.subject, 'Ask for price, test for wizard')
        self.assertEqual(product, thread.product)

class AlertWizardTest(TestCase):
    fixtures = ['patron', 'address', 'category']
    
    def test_zero_step(self):
        response = self.client.get(reverse('alert_create'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/alert_create.html')
    
    def test_first_step_as_anonymous(self):
        response = self.client.post(reverse('alert_create'), {
            '0-designation': 'Perceuse',
            '0-description': 'J ai besoin d une perceuse pour percer des trou dans le béton'
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/alert_register.html')

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('alert_create'), {
            '0-designation': 'Perceuse',
            '0-description': 'J ai besoin d une perceuse pour percer des trou dans le béton',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/alert_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('alert_create'), {
            '0-designation': 'Perceuse',
            '0-description': 'J ai besoin d une perceuse pour percer des trou dans le béton',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '7, rue claude chahu',
            '2-addresses__zipcode': '75016',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        self.assertRedirects(response, reverse('alert_edit'))


