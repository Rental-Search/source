# -*- coding: utf-8 -*-
import datetime

from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from facebook import GraphAPIError, GraphAPI

from eloue.products.models import Product
from eloue.rent.models import Booking
from eloue.wizard import MultiPartFormWizard
from eloue.accounts.models import FacebookSession, Patron
from eloue.accounts.models import CreditCard
from eloue.payments.paybox_payment import PayboxManager, PayboxException

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

class BookingWizardTestWithFacebookAsAnonymous(BookingWizardTestWithFacebook):
    me = {
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

    def __init__(self, *args, **kwargs):
        super(BookingWizardTestWithFacebookAsAnonymous, self).__init__(*args, **kwargs)
        self.access_token = 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD'
        self.uid = 100003207275288

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me

        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
        self.assertTrue(mock_object.called)
    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
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
        self.assertTrue(mock_object.called)
    
    @patch.object(PayboxManager, 'unsubscribe')
    @patch.object(PayboxManager, 'authorize_subscribed')
    @patch.object(PayboxManager, 'subscribe')
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fourth_step_as_anonymous(self, mock_hash, mock_object, mock_subscribe, mock_authorize,mock_unsubscribe):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        mock_authorize.return_value = ('0001234', '0002345')
        mock_subscribe.return_value = 'SLDLrcsLMPC'
        mock_unsubscribe.return_value = None
        
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            '3-cvv': '123',
            '3-expires_0': '12',
            '3-expires_1': '20',
            '3-card_number': '1111222233334444',
            '3-keep': True,
            '3-holder_name': 'xxx',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        self.assertRedirects(response, reverse('booking_success', kwargs={'booking_id': Booking.objects.get().pk.hex}))
        self.assertEquals(CreditCard.objects.count(), 1)
        cc = CreditCard.objects.get()
        self.assertEquals(cc.masked_number, '1XXXXXXXXXXXX444')
        self.assertEqual(cc.card_number, 'SLDLrcsLMPC')
        self.assertTrue(mock_object.called)
        cc.delete()


class BookingWizardTestWithFacebookAsNew(BookingWizardTestWithFacebook):
    me = {
        u'email': u'kosii.spam@gmail.com',
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

    def __init__(self, *args, **kwargs):
        super(BookingWizardTestWithFacebookAsNew, self).__init__(*args, **kwargs)
        self.access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        self.uid = 100000609837182

    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_new(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
        self.assertTrue(mock_object.called)
    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_new(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
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
        self.assertTrue(mock_object.called)
    
    @patch.object(PayboxManager, 'authorize_subscribed')
    @patch.object(PayboxManager, 'subscribe')
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fifth_step_as_new(self, mock_hash, mock_object, mock_subscribe, mock_authorize):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        mock_authorize.return_value = ('0001234', '0002345')
        mock_subscribe.return_value = 'SLLLqssDLLS'
        
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            '2-username': 'kosii2',
            '2-first_name': 'first',
            '2-last_name': 'last',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            '3-cvv': '123',
            '3-expires_0': '12',
            '3-expires_1': '20',
            '3-card_number': '1111222233334444',
            '3-holder_name': 'xxx',
            '3-keep': False,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        self.assertTrue(mock_object.called)
        self.assertRedirects(response, reverse('booking_success', kwargs={'booking_id': Booking.objects.get().pk.hex}))

    @patch.object(PayboxManager, 'authorize_subscribed')
    @patch.object(PayboxManager, 'authorize')
    @patch.object(PayboxManager, 'subscribe')
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fifth_step_as_new_fail(self, mock_hash, mock_object, mock_subscribe, mock_authorize, mock_authorize_subscribed):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        mock_subscribe.return_value = 'SLLLqssDLLS'
        mock_authorize.return_value = ('0001234', '0002345')
        mock_authorize_subscribed.side_effect = PayboxException('016', '')

        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            '2-username': 'kosii2',
            '2-first_name': 'first',
            '2-last_name': 'last',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            '3-cvv': '123',
            '3-expires_0': '12',
            '3-expires_1': '20',
            '3-card_number': '1111222233334444',
            '3-holder_name': 'xxx',
            '3-keep': False,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_subscribe.called)
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_authorize_subscribed.called)
        self.assertTrue(mock_object.called)
        self.assertRedirects(response, reverse('booking_failure', kwargs={'booking_id': Booking.objects.get().pk.hex}))

class BookingWizardTestWithFacebookAssociate(BookingWizardTestWithFacebook):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'facebooksession']
    
    me = {u'email': u'elouetest@gmail.com',
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

    def __init__(self, *args, **kwargs):
        super(BookingWizardTestWithFacebookAssociate, self).__init__(*args, **kwargs)
        self.access_token = 'AAAC0EJC00lQBAFeztcpDKBgyFDRm9kIiaSe7amtYzcw2MLiSdfEeh9ftpZAFzYUT0zwIqXCnBEYe95I1cnMX8dZCQ2Dw10qJlhJRgYxgZDZD'
        self.uid = 100003190074813


    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_associate(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        
        self.assertEqual(FacebookSession.objects.get(uid=self.uid).user, None)
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
        self.assertTrue(mock_object.called)
    
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_associate(self, mock_method, mock_object):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        
        self.assertEqual(FacebookSession.objects.get(uid=self.uid).user, None)
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
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
        self.assertTrue(mock_object.called)
    
    @patch.object(PayboxManager, 'authorize_subscribed')
    @patch.object(PayboxManager, 'subscribe')
    @patch.object(GraphAPI, 'get_object')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fifth_step_associate(self, mock_hash, mock_object, mock_subscribe, mock_authorize):
        mock_hash.return_value = '6941fd7b20d720833717a1f92e8027af'
        mock_object.return_value = self.me
        mock_authorize.return_value = ('0001234', '0002345')
        mock_subscribe.return_value = 'SLLLqssDLLS'
        
        self.assertEqual(FacebookSession.objects.get(uid=self.uid).user, None)
        response = self.client.post(reverse('booking_create', args=['location/bebe/mobilier-bebe/lits/', self.product.slug, self.product.id]), {
            '0-started_at_0': '18/10/2010',
            '0-started_at_1': '08:00:00',
            '0-ended_at_0': '19/10/2010',
            '0-ended_at_1': '08:00:00',
            '0-quantity': 1,
            '1-email': '',
            '1-exists': 1,
            '1-password': '',
            '1-facebook_access_token': self.access_token,
            '1-facebook_expires': 0,
            '1-facebook_uid': self.uid,
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            '3-cvv': '123',
            '3-expires_0': '12',
            '3-expires_1': '20',
            '3-card_number': '1111222233334444',
            '3-holder_name': 'xxx',
            '3-keep': False,
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        self.assertRedirects(response, reverse('booking_success', kwargs={'booking_id': Booking.objects.get().pk.hex}))
        self.assertEqual(FacebookSession.objects.get(uid=self.uid).user, Patron.objects.get(username='kosii1'))
        self.assertTrue(mock_object.called)

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
        self.assertTemplateUsed(response, 'accounts/auth_login.html')
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
        self.assertTemplateUsed(response, 'accounts/auth_missing.html')
    
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
    

    @patch.object(PayboxManager, 'authorize_subscribed')
    @patch.object(PayboxManager, 'subscribe')
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_fifth_step_as_anonymous(self, mock_hash, mock_subscribe, mock_authorize):
        mock_authorize.return_value = ('0001234', '0002345')
        mock_subscribe.return_value = 'SLLLqssDLLS'
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
            '3-cvv': '123',
            '3-expires_0': '12',
            '3-expires_1': '20',
            '3-card_number': '1111222233334444',
            '3-keep': False,
            '3-holder_name': 'xxx',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'hash_2': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 3
        })
        self.assertTrue(mock_authorize.called)
        self.assertTrue(mock_subscribe.called)
        booking = Booking.objects.get()
        self.assertRedirects(response, reverse('booking_success', kwargs={'booking_id': booking.pk.hex}))

    def tearDown(self):
        datetime.datetime = self.old_datetime



