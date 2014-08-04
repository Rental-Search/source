# -*- coding: utf-8 -*-
import os.path
import base64

from django.db.models import get_model
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from rest_framework.test import APITestCase

User = get_user_model()

def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)

class AnonymousUsersTest(APITestCase):
    def test_location(self):
        self.assertEqual(_location('patron-reset-password', pk=2222), '/api/2.0/users/2222/reset_password/')

    def test_account_anonymous_access_forbidden(self):
        response = self.client.get(_location('patron-list'))
        self.assertEquals(response.status_code, 401)

    def test_account_anonymous_creation_required(self):
        post_data = {
            'username': 'chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com',
        }
        response = self.client.post(_location('patron-list'), post_data)
        self.assertEquals(response.status_code, 201, response.data)

        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('patron-detail', pk=response.data['id'])), response['Location'])

        user = User.objects.get(pk=response.data['id'])
        # check password has been applied
        self.assertTrue(user.check_password('begood'))
        # check provided fields have been applied
        self.assertEquals(user.username, 'chuck')
        self.assertEquals(user.email, 'chuck.berry@chess-records.com')
        # check flags and other auto-set fields
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_account_anonymous_creation_languages(self):
        post_data = {
            'username': 'chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com',
            'languages': [22, 51],
        }
        response = self.client.post(_location('patron-list'), post_data)
        self.assertEquals(response.status_code, 201, response.data)

class UsersTest(APITestCase):
    fixtures = ['patron']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_account_password_change_ok(self, method='post'):
        response = getattr(self.client, method)(_location('patron-reset-password', pk=1), {
            'current_password': 'alexandre',
            'password': 'alex',
            'confirm_password': 'alex'
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEquals(response.data['detail'], _(u"Votre mot de passe à bien été modifié"))
        # check that password has been changed in DB
        self.assertTrue(User.objects.get(pk=1).check_password('alex'))

    def test_account_password_reset_put(self):
        self.test_account_password_change_ok(method='put')

    def test_account_password_reset_nok(self):
        response = self.client.post(_location('patron-reset-password', pk=1), {
            'current_password': 'lalala',
            'password': 'hehehe',
            'confirm_password': 'hahaha'
        })
        self.assertEquals(response.status_code, 400)
        self.assertIn('errors', response.data)
        errors = response.data['errors']
        self.assertIn(_("Your current password was entered incorrectly. Please enter it again."), errors['current_password'])
        self.assertIn(_("The two password fields didn't match."), errors['confirm_password'])
        # check that password has NOT been changed in DB
        self.assertTrue(User.objects.get(pk=1).check_password('alexandre'))

    def test_account_password_edit_unavailable(self):
        response = self.client.put(_location('patron-detail', pk=1), {
            'password': 'hehehe',
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertNotIn('password', response.data)
        # check that password has NOT been changed in DB
        self.assertTrue(User.objects.get(pk=1).check_password('alexandre'))

    def test_account_detail_authz_end_user(self):
        # check we have access to own User record
        response = self.client.get(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 200)
        # check we do NOT have access to other User records
        response = self.client.get(_location('patron-detail', pk=2))
        self.assertEquals(response.status_code, 404)

    def test_account_avatar_upload_multipart(self):
        self.assertFalse(User.objects.get(pk=1).avatar)
        with open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'avatar.png'), 'rb') as image:
            response = self.client.put(_location('patron-detail', pk=1), {
                'avatar': image,
            }, format='multipart')
            self.assertEquals(response.status_code, 200, response.data)
            self.assertTrue(User.objects.get(pk=1).avatar)

    def test_account_avatar_upload_base64(self):
        self.assertFalse(User.objects.get(pk=1).avatar)
        filename = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'avatar.png')
        with open(filename, 'rb') as image:
            response = self.client.put(_location('patron-detail', pk=1), {
                'avatar': {
                    'content': base64.b64encode(image.read()),
                    'filename': os.path.basename(filename),
                    #'encoding': 'base64',
                }
            })
            self.assertEquals(response.status_code, 200, response.data)
            self.assertTrue(User.objects.get(pk=1).avatar)

    def test_account_avatar_upload_url(self):
        self.assertFalse(User.objects.get(pk=1).avatar)
        response = self.client.put(_location('patron-detail', pk=1), {
            'avatar': {
                'content': 'http://liyaliao.weebly.com/uploads/1/5/2/9/15298970/6065967.jpg',
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertTrue(User.objects.get(pk=1).avatar)

    def test_account_get_me(self):
        self.assertFalse(User.objects.get(pk=1).avatar)
        response = self.client.get(_location('patron-detail', pk='me'))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEquals(response.data['id'], 1)

    def test_account_delete(self):
        self.assertEquals(User.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(User.objects.filter(pk=1).count(), 0)

    def test_account_list_paginated(self):
        response = self.client.get(_location('patron-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 1, # we should get only 1 account visible for the current user (pk=1); it must be himself
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))
        self.assertEquals(response.data['results'][0]['id'], 1)

class PhoneNumbersTest(APITestCase):
    fixtures = ['patron', 'phones']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_phonenumber_premium_rate_number(self):
        response = self.client.get(_location('phonenumber-premium-rate-number', pk=1))
        self.assertEquals(response.status_code, 200)
        self.assertIn('numero', response.data)
        number = response.data['numero']
        self.assertTrue(isinstance(number, basestring) and len(number))

    def test_phonenumber_create(self):
        response = self.client.post(_location('phonenumber-list'), {
            'number': '0198765432',
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        # the currently authenticated user must be used on creation
        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('phonenumber-detail', pk=response.data['id'])))

    def test_phonenumber_delete(self):
        PhoneNumber = get_model('accounts', 'PhoneNumber')
        self.assertEquals(PhoneNumber.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('phonenumber-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(PhoneNumber.objects.filter(pk=1).count(), 0)

    def test_phonenumber_edit_number(self):
        response = self.client.put(_location('phonenumber-detail', pk=1), {
            'number': '0198765432',
        })
        self.assertEquals(response.status_code, 200, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        self.assertEquals(response.data['number'], '0198765432')

    def test_phonenumber_list_paginated(self):
        response = self.client.get(_location('phonenumber-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 1, # we should get 1 phone number (from 2 in total) visible for the current user (pk=1)
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))

class AddressesTest(APITestCase):
    fixtures = ['patron', 'address']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_address_create(self):
        response = self.client.post(_location('address-list'), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        # the currently authenticated user must be used on creation
        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))
        # 'street' is stored in 2 different fields in the model: address1 and address2
        self.assertEquals(response.data['street'], '2, rue debelleyme')
        # 'position' is expected to be automatically calculated based on city+address+country info by the model 
        self.assertEquals(response.data['position']['coordinates'], [48.8603858, 2.3645553])
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('address-detail', pk=response.data['id'])))

    def test_address_delete(self):
        Address = get_model('accounts', 'Address')
        self.assertEquals(Address.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('address-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(Address.objects.filter(pk=1).count(), 0)

    def test_address_edit_street(self):
        response = self.client.put(_location('address-detail', pk=1), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
        })
        self.assertEquals(response.status_code, 200, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        # 'street' is stored in 2 different fields in the model: address1 and address2
        self.assertEquals(response.data['street'], '2, rue debelleyme')
        # 'position' is expected to be automatically calculated based on city+address+country info by the model 
        self.assertEquals(response.data['position']['coordinates'], [48.8603858, 2.3645553])

    def test_address_list_paginated(self):
        response = self.client.get(_location('address-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 2, # we should get 2 addresses (from 3 in total) visible for the current user (pk=1)
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))
