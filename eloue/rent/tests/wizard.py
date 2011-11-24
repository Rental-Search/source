# -*- coding: utf-8 -*-
import datetime

from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from eloue.products.models import Product
from eloue.rent.models import Booking
from eloue.wizard import MultiPartFormWizard
from eloue.accounts.models import FacebookSession, Patron

class BookingMock(Booking):
    def preapproval(self, *args, **kwargs):
        pass
    

class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return datetime.datetime(2010, 8, 15, 9, 0)

class BookingWizardTestWithFacebook(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'facebooksession']
    
    def setUp(self):
        self.product = Product.objects.get(pk=1)
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime


    def tearDown(self):
        datetime.datetime = self.old_datetime

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD'
        uid = 100003207275288
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
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
        self.assertTemplateUsed(response, 'rent/booking_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD'
        uid = 100003207275288
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'rent/booking_confirm.html')
    
    @patch.object(Booking, 'preapproval')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fourth_step_as_anonymous(self, mock_hash, mock_preapproval):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD'
        uid = 100003207275288
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_preapproval.called)

#---------------------------------

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_new(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        uid = 100000609837182
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
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
        self.assertTemplateUsed(response, 'rent/booking_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_new(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        uid = 100000609837182
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-username': 'kosii2',
            '2-first_name': 'first',
            '2-last_name': 'last',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'rent/booking_confirm.html')
    
    @patch.object(Booking, 'preapproval')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fourth_step_as_new(self, mock_hash, mock_preapproval):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        uid = 100000609837182
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-username': 'kosii2',
            '2-first_name': 'first',
            '2-last_name': 'last',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_preapproval.called)

#---------------------------------

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_associate(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        uid = 100003190074813
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, None)
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
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
        self.assertTemplateUsed(response, 'rent/booking_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_associate(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        uid = 100003190074813
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, None)
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'rent/booking_confirm.html')
    
    @patch.object(Booking, 'preapproval')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fourth_step_associate(self, mock_hash, mock_preapproval):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        uid = 100003190074813
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, None)
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': uid,
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_preapproval.called)
        self.assertEqual(FacebookSession.objects.get(uid=uid).user, Patron.objects.get(username='kosii1'))

class BookingWizardTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def setUp(self):
        self.product = Product.objects.get(pk=1)
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime
    
    def test_zero_step(self):
        response = self.client.get(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]))
        self.assertEquals(response.status_code, 200)
    
    def test_zero_step_archived(self):
        self.product.is_archived = True
        self.product.save()
        response = self.client.get(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]))
        self.assertEquals(response.status_code, 404)
    
    def test_zero_step_allowed(self):
        self.product.is_allowed = False
        self.product.save()
        response = self.client.get(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]))
        self.assertEquals(response.status_code, 404)
    
    def test_zero_step_redirect(self):
        response = self.client.get(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', 'perceuse-visseuse', self.product.id]))
        self.assertRedirects(response, reverse('booking_create', args=['bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), status_code=301)
    
    def test_first_step_as_anonymous(self):
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'rent/booking_register.html')
        self.assertEquals(response.context['preview']['started_at'], datetime.datetime(2010, 10, 18, 8, 0))
        self.assertEquals(response.context['preview']['ended_at'], datetime.datetime(2010, 10, 19, 8, 0))
        self.assertTrue('total_amount' in response.context['preview'])
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'rent/booking_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
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
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'rent/booking_confirm.html')
    
    @patch.object(Booking, 'preapproval')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fourth_step_as_anonymous(self, mock_hash, mock_preapproval):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': 'timothee.peignier@e-loue.com',
            '1-exists': 1,
            '1-password': 'timothee',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_preapproval.called)
    
    def tearDown(self):
        datetime.datetime = self.old_datetime



