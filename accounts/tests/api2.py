# -*- coding: utf-8 -*-
import os.path
import base64
import datetime
from decimal import Decimal

from django.db.models import get_model
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from rest_framework.test import APITestCase


def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)


class AnonymousUsersTest(APITestCase):

    fixtures = ['patron']

    public_fields = (
        'id', 'company_name', 'username', 'is_professional', 'slug', 'avatar', 'default_address', 'about', 'work',
        'school', 'hobby', 'languages', 'url', 'date_joined')
    private_fields = (
        'email', 'first_name', 'last_name', 'default_number', 'driver_license_date', 'driver_license_number',
        'date_of_birth', 'place_of_birth', 'is_active')

    def setUp(self):
        self.model = get_user_model()

    def test_location(self):
        self.assertEqual(_location('patron-reset-password', pk=2222), '/api/2.0/users/2222/reset_password/')

    def test_account_list_forbidden(self):
        response = self.client.get(_location('patron-list'))
        self.assertEquals(response.status_code, 401)

    def test_account_search_allowed(self):
        response = self.client.get(_location('patron-list'), {
            'username': 'alexandre'
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        data = response.data['results'][0]

        for field in self.public_fields:
            self.assertIn(field, data, field)

        for field in self.private_fields:
            self.assertNotIn(field, data, field)

    def test_account_show_allowed(self):
        response = self.client.get(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_account_update_forbidden(self):
        response = self.client.put(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_account_delete_forbidden(self):
        response = self.client.delete(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_account_reset_password_forbidden(self):
        response = self.client.put(_location('patron-reset-password', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_account_create_no_fields(self):
        response = self.client.post(_location('patron-list'))
        self.assertEqual(response.status_code, 400)

        required_fields = ('email', 'username', 'password')
        for field in required_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_account_create_required_fields(self):
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
        self.assertTrue(
            response['Location'].endswith(_location('patron-detail', pk=response.data['id'])),
            response['Location'])

        user = self.model.objects.get(pk=response.data['id'])
        # check password has been applied
        self.assertTrue(user.check_password('begood'))
        # check provided fields have been applied
        self.assertEquals(user.username, 'chuck')
        self.assertEquals(user.email, 'chuck.berry@chess-records.com')
        # check flags and other auto-set fields
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_account_create_all_fields(self):
        post_data = {
            'username': 'test_user',
            'password': '123456',
            'email': 'mailbox@mailserver.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'ACME',
            'is_professional': True,
            'about': 'Some text',
            'work': 'Some work',
            'school': 'Some school',
            'driver_license_date': '2010-01-01 00:00',
            'driver_license_number': '123456',
            'date_of_birth': '1980-01-01 00:00',
            'place_of_birth': 'Earth',
            'rib': 'Some rib',
            'url': 'http://www.website.com'
        }
        response = self.client.post(_location('patron-list'), post_data)
        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(
            response['Location'].endswith(_location('patron-detail', pk=response.data['id'])),
            response['Location'])

        user = self.model.objects.get(pk=response.data['id'])
        self.assertTrue(user.check_password('123456'))
        self.assertEquals(user.username, 'test_user')
        self.assertEquals(user.email, 'mailbox@mailserver.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.company_name, 'ACME')
        self.assertTrue(user.is_professional)
        self.assertEqual(user.about, 'Some text')
        self.assertEqual(user.work, 'Some work')
        self.assertEqual(user.school, 'Some school')
        self.assertEqual(user.drivers_license_date, datetime.datetime(2010, 1, 1))
        self.assertEqual(user.drivers_license_number, '123456')
        self.assertEqual(user.date_of_birth, datetime.datetime(1980, 1, 1))
        self.assertEqual(user.place_of_birth, 'Earth')
        self.assertEqual(user.rib, 'Some rib')
        self.assertEqual(user.url, 'http://www.website.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_account_create_languages(self):
        post_data = {
            'username': 'chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com',
            'languages': [22, 51],
        }
        response = self.client.post(_location('patron-list'), post_data)
        self.assertEquals(response.status_code, 201, response.data)

    def test_account_create_wrong_email(self):
        post_data = {
            'username': 'John',
            'password': 'Doe',
            'email': 'mailbox.mailserver.com',
        }
        response = self.client.post(_location('patron-list'), post_data)
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('email', response.data['errors'], response.data)


class UsersTest(APITestCase):
    fixtures = ['patron']
    image_file = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'avatar.png')
    image_url = 'http://eloue.s3.amazonaws.com/static/images/default_avatar.png'

    def setUp(self):
        self.model = get_user_model()
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
        self.assertTrue(self.model.objects.get(pk=1).check_password('alex'))

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
        self.assertTrue(self.model.objects.get(pk=1).check_password('alexandre'))

    def test_account_password_edit_unavailable(self):
        response = self.client.put(_location('patron-detail', pk=1), {
            'password': 'hehehe',
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertNotIn('password', response.data)
        # check that password has NOT been changed in DB
        self.assertTrue(self.model.objects.get(pk=1).check_password('alexandre'))

    def test_account_detail_authz_end_user(self):
        # check we have access to own User record
        response = self.client.get(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 200)
        # check we also have read-only access to other User records
        response = self.client.get(_location('patron-detail', pk=2))
        self.assertEquals(response.status_code, 200)

    def test_account_avatar_upload_multipart(self):
        self.assertFalse(self.model.objects.get(pk=1).avatar)
        with open(self.image_file, 'rb') as image:
            response = self.client.put(_location('patron-detail', pk=1), {
                'avatar': image,
            }, format='multipart')
            self.assertEquals(response.status_code, 200, response.data)
            self.assertTrue(self.model.objects.get(pk=1).avatar)
            self.assertIn('avatar', response.data, response.data)
            for k in ('thumbnail', 'profil', 'display', 'product_page'):
                self.assertIn(k, response.data['avatar'], response.data)
                self.assertTrue(response.data['avatar'][k], response.data)

    def test_account_avatar_upload_base64(self):
        self.assertFalse(self.model.objects.get(pk=1).avatar)
        with open(self.image_file, 'rb') as image:
            response = self.client.put(_location('patron-detail', pk=1), {
                'avatar': {
                    'content': base64.b64encode(image.read()),
                    'filename': os.path.basename(self.image_file),
                    #'encoding': 'base64',
                }
            })
            self.assertEquals(response.status_code, 200, response.data)
            self.assertTrue(self.model.objects.get(pk=1).avatar)
            self.assertIn('avatar', response.data, response.data)
            for k in ('thumbnail', 'profil', 'display', 'product_page'):
                self.assertIn(k, response.data['avatar'], response.data)
                self.assertTrue(response.data['avatar'][k], response.data)

    def test_account_avatar_upload_url(self):
        self.assertFalse(self.model.objects.get(pk=1).avatar)
        response = self.client.put(_location('patron-detail', pk=1), {
            'avatar': {
                'content': self.image_url,
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertTrue(self.model.objects.get(pk=1).avatar)
        self.assertIn('avatar', response.data, response.data)
        for k in ('thumbnail', 'profil', 'display', 'product_page'):
            self.assertIn(k, response.data['avatar'], response.data)
            self.assertTrue(response.data['avatar'][k], response.data)

    def test_account_get_me(self):
        self.assertFalse(self.model.objects.get(pk=1).avatar)
        response = self.client.get(_location('patron-detail', pk='me'))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEquals(response.data['id'], 1)

    def test_account_delete(self):
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('patron-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(self.model.objects.filter(pk=1).count(), 0)

    def test_account_list_paginated(self):
        response = self.client.get(_location('patron-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 1,  # we should get only 1 account visible for the current user (pk=1); it must be himself
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))
        self.assertEquals(response.data['results'][0]['id'], 1)

    def test_account_edit_me(self):
        response = self.client.patch(_location('patron-detail', pk='me'), {
            'first_name': 'prenom',
            'last_name': 'nom',
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEquals(response.data['id'], 1)
        self.assertEquals(response.data['first_name'], 'prenom')
        self.assertEquals(response.data['last_name'], 'nom')

    def test_account_update_all_fields(self):
        user = self.model.objects.get(pk=1)
        self.assertNotEquals(user.username, 'test_user')
        self.assertNotEquals(user.email, 'mailbox@mailserver.com')
        self.assertNotEqual(user.company_name, 'ACME')
        self.assertFalse(user.is_professional)
        self.assertNotEqual(user.about, 'Some text')
        self.assertNotEqual(user.work, 'Some work')
        self.assertNotEqual(user.school, 'Some school')
        self.assertNotEqual(user.drivers_license_date, datetime.datetime(2010, 1, 1))
        self.assertNotEqual(user.drivers_license_number, '123456')
        self.assertNotEqual(user.date_of_birth, datetime.datetime(1980, 1, 1))
        self.assertNotEqual(user.place_of_birth, 'Earth')
        self.assertNotEqual(user.rib, 'Some rib')
        self.assertNotEqual(user.url, 'http://www.website.com')

        data = {
            'username': 'test_user',
            'email': 'mailbox@mailserver.com',
            'company_name': 'ACME',
            'is_professional': True,
            'about': 'Some text',
            'work': 'Some work',
            'school': 'Some school',
            'driver_license_date': '2010-01-01 00:00',
            'driver_license_number': '123456',
            'date_of_birth': '1980-01-01 00:00',
            'place_of_birth': 'Earth',
            'rib': 'Some rib',
            'url': 'http://www.website.com'
        }
        response = self.client.patch(_location('patron-detail', pk=1), data)
        self.assertEquals(response.status_code, 200, response.data)

        user = self.model.objects.get(pk=1)
        self.assertEquals(user.username, 'test_user')
        self.assertEquals(user.email, 'mailbox@mailserver.com')
        self.assertEqual(user.company_name, 'ACME')
        self.assertTrue(user.is_professional)
        self.assertEqual(user.about, 'Some text')
        self.assertEqual(user.work, 'Some work')
        self.assertEqual(user.school, 'Some school')
        self.assertEqual(user.drivers_license_date, datetime.datetime(2010, 1, 1))
        self.assertEqual(user.drivers_license_number, '123456')
        self.assertEqual(user.date_of_birth, datetime.datetime(1980, 1, 1))
        self.assertEqual(user.place_of_birth, 'Earth')
        self.assertEqual(user.rib, 'Some rib')
        self.assertEqual(user.url, 'http://www.website.com')


class AnonymousPhoneNumbersTest(APITestCase):

    fixtures = ['phone_patron', 'phones']

    def test_phonenumber_list_forbidden(self):
        response = self.client.get(_location('phonenumber-list'))
        self.assertEquals(response.status_code, 401)

    def test_phonenumber_show_forbidden(self):
        response = self.client.get(_location('phonenumber-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_phonenumber_create_forbidden(self):
        response = self.client.post(_location('phonenumber-list'))
        self.assertEquals(response.status_code, 401)

    def test_phonenumber_update_forbidden(self):
        response = self.client.put(_location('phonenumber-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_phonenumber_delete_forbidden(self):
        response = self.client.delete(_location('phonenumber-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_phonenumber_premium_rate_number_allowed(self):
        response = self.client.get(_location('phonenumber-premium-rate-number', pk=1))
        self.assertEquals(response.status_code, 200)
        self.assertIn('numero', response.data)
        number = response.data['numero']
        self.assertTrue(isinstance(number, basestring) and len(number))


class PhoneNumberTest(APITestCase):
    fixtures = ['phone_patron', 'phone_api2', 'address', 'phone_product', 'category']

    def setUp(self):
        self.model = get_model('accounts', 'PhoneNumber')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_phonenumber_premium_rate_number(self):
        response = self.client.get(_location('phonenumber-premium-rate-number', pk=1))
        self.assertEquals(response.status_code, 200)
        self.assertIn('numero', response.data)
        number = response.data['numero']
        self.assertTrue(isinstance(number, basestring) and len(number))

    def test_phonenumber_create_no_fields(self):
        response = self.client.post(_location('phonenumber-list'))
        self.assertEquals(response.status_code, 400, response.data)

        required_fields = {'patron', 'number'}
        default_fields = {'patron'}
        for field in required_fields - default_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_phonenumber_create_required_fields(self):
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

    def test_phonenumber_create_all_fields(self):
        response = self.client.post(_location('phonenumber-list'), {
            'number': '0198765432',
            'patron': _location('patron-detail', pk=1)
        })
        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('phonenumber-detail', pk=response.data['id'])))

        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))
        self.assertEquals(response.data['number'], '0198765432')

    def test_phonenumber_create_not_mine(self):
        response = self.client.post(_location('phonenumber-list'), {
            'number': '0198765432',
            'patron': _location('patron-detail', pk=2)
        })
        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('phonenumber-detail', pk=response.data['id'])))

        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))
        self.assertEquals(response.data['number'], '0198765432')

    def test_phonenumber_delete(self):
        self.assertEquals(self.model.objects.filter(pk=4).count(), 1)
        response = self.client.delete(_location('phonenumber-detail', pk=4))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(self.model.objects.filter(pk=4).count(), 0)

    def test_phonenumber_used_in_account_delete(self):
        self.assertEquals(self.model.objects.filter(pk=3).count(), 1)
        response = self.client.delete(_location('phonenumber-detail', pk=3))
        self.assertEquals(response.status_code, 400, response.data)
        self.assertEquals(self.model.objects.filter(pk=3).count(), 1)

    def test_phonenumber_used_in_product_delete(self):
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('phonenumber-detail', pk=1))
        self.assertEquals(response.status_code, 400, response.data)
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)

    def test_phonenumber_delete_not_mine(self):
        self.assertEquals(self.model.objects.filter(pk=2).count(), 1)
        response = self.client.delete(_location('phonenumber-detail', pk=2))
        self.assertEquals(response.status_code, 404, response.data)
        self.assertEquals(self.model.objects.filter(pk=2).count(), 1)

    def test_phonenumber_edit_number(self):
        response = self.client.put(_location('phonenumber-detail', pk=1), {
            'number': '0198765432',
        })
        self.assertEquals(response.status_code, 200, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        self.assertEquals(response.data['number'], '0198765432')

    def test_phonenumber_edit_not_mine(self):
        response = self.client.put(_location('phonenumber-detail', pk=2), {
            'number': '0198765432',
        })
        self.assertEqual(response.status_code, 404, response.data)

    def test_phonenumber_edit_change_owner(self):
        response = self.client.patch(_location('phonenumber-detail', pk=1), {
            'patron': _location('patron-detail', pk=2)
        })
        self.assertEqual(response.status_code, 200, response.data)
        # End user can't create record for other person. Owner is force set as current user.
        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))

    def test_phonenumber_list_paginated(self):
        response = self.client.get(_location('phonenumber-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 3,  # we should get 1 phone number (from 2 in total) visible for the current user (pk=1)
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))

    def test_edit_default_address(self):
        response = self.client.get(_location('patron-detail', pk='me'))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)
        self.assertEquals(response.data['id'], 1)
        user_id = response.data['id']

        # create a new Address record
        response = self.client.post(_location('address-list'), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        address_id = response.data['id']

        # set the Address record we've just created as the 'default_address' attribute
        response = self.client.patch(_location('patron-detail', pk=user_id), {
            'default_address': _location('address-detail', pk=address_id),
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('default_address', response.data, response.data)
        self.assertTrue(len(response.data['default_address']), response.data['default_address'])
        self.assertEquals(response.data['default_address']['id'], address_id, response.data)

    def test_edit_default_phone_number(self):
        response = self.client.get(_location('patron-detail', pk='me'))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)
        self.assertEquals(response.data['id'], 1)
        user_id = response.data['id']

        # create a new PhoneNumber record
        response = self.client.post(_location('phonenumber-list'), {
            'number': '0198765432',
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        phonenumber_id = response.data['id']

        # set the PhoneNumber record we've just created as the 'default_number' attribute
        response = self.client.patch(_location('patron-detail', pk=user_id), {
            'default_number': _location('phonenumber-detail', pk=phonenumber_id),
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('default_number', response.data, response.data)
        self.assertTrue(len(response.data['default_number']), response.data['default_number'])
        self.assertEquals(response.data['default_number']['id'], phonenumber_id, response.data)


class AnonymousAddressesTest(APITestCase):

    fixtures = ['address_patron', 'address']

    public_fields = ('zipcode', 'position', 'city', 'country')
    private_fields = ('patron', 'id', 'street')

    def test_address_list_forbidden(self):
        response = self.client.get(_location('address-list'))
        self.assertEquals(response.status_code, 401)

    def test_address_show_allowed(self):
        response = self.client.get(_location('address-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_address_create_forbidden(self):
        response = self.client.post(_location('address-list'))
        self.assertEquals(response.status_code, 401)

    def test_address_update_forbidden(self):
        response = self.client.put(_location('address-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_address_delete_forbidden(self):
        response = self.client.delete(_location('address-detail', pk=1))
        self.assertEquals(response.status_code, 401)


class AddressTest(APITestCase):
    fixtures = ['address_patron', 'address_api2', 'product', 'category']

    def setUp(self):
        self.model = get_model('accounts', 'Address')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_address_create_no_fields(self):
        response = self.client.post(_location('address-list'))
        self.assertEquals(response.status_code, 400, response.data)

        required_fields = {'patron', 'street', 'zipcode', 'city', 'country'}
        default_fields = {'patron'}
        for field in required_fields - default_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_address_create_required_fields(self):
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

    def test_address_create_all_fields(self):
        response = self.client.post(_location('address-list'), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
            'patron': _location('patron-detail', pk=1)
        })
        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('address-detail', pk=response.data['id'])))

        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))
        self.assertEquals(response.data['street'], '2, rue debelleyme')
        self.assertEquals(response.data['position']['coordinates'], [48.8603858, 2.3645553])

    def test_address_create_not_mine(self):
        response = self.client.post(_location('address-list'), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
            'patron': _location('patron-detail', pk=2)
        })
        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('address-detail', pk=response.data['id'])))

        # End user can't create record for other person. Owner is force set as current user.
        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))
        self.assertEquals(response.data['street'], '2, rue debelleyme')
        self.assertEquals(response.data['position']['coordinates'], [48.8603858, 2.3645553])

    def test_address_create_wrong_country(self):
        response = self.client.post(_location('address-list'), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'Neverland',
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('country', response.data['errors'])

    def test_address_delete(self):
        self.assertEquals(self.model.objects.filter(pk=4).count(), 1)
        response = self.client.delete(_location('address-detail', pk=4))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(self.model.objects.filter(pk=4).count(), 0)

    def test_address_used_in_account_delete(self):
        self.assertEquals(self.model.objects.filter(pk=3).count(), 1)
        response = self.client.delete(_location('address-detail', pk=3))
        self.assertEquals(response.status_code, 400, response.data)
        self.assertEquals(self.model.objects.filter(pk=3).count(), 1)

    def test_address_used_in_product_delete(self):
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('address-detail', pk=1))
        self.assertEquals(response.status_code, 400, response.data)
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)

    def test_address_delete_not_mine(self):
        self.assertEquals(self.model.objects.filter(pk=2).count(), 1)
        response = self.client.delete(_location('address-detail', pk=2))
        self.assertEquals(response.status_code, 404, response.data)
        self.assertEquals(self.model.objects.filter(pk=2).count(), 1)

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

    def test_address_edit_not_mine(self):
        response = self.client.put(_location('address-detail', pk=2), {
            'city': 'Paris',
            'street': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
        })
        self.assertEqual(response.status_code, 404, response.data)

    def test_address_edit_change_owner(self):
        response = self.client.patch(_location('address-detail', pk=1), {
            'patron': _location('patron-detail', pk=2)
        })
        self.assertEqual(response.status_code, 200, response.data)
        # End user can't create record for other person. Owner is force set as current user.
        self.assertTrue(response.data['patron'].endswith(_location('patron-detail', pk=1)))

    def test_address_list_paginated(self):
        response = self.client.get(_location('address-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 3,  # we should get 2 addresses (from 3 in total) visible for the current user (pk=1)
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))


class AnonymousCreditCardTest(APITestCase):

    fixtures = ['patron', 'creditcard']

    def test_creditcard_list_forbidden(self):
        response = self.client.get(_location('creditcard-list'))
        self.assertEquals(response.status_code, 401)

    def test_creditcard_show_forbidden(self):
        response = self.client.get(_location('creditcard-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_creditcard_create_forbidden(self):
        response = self.client.post(_location('creditcard-list'))
        self.assertEquals(response.status_code, 401)

    def test_creditcard_delete_forbidden(self):
        response = self.client.delete(_location('creditcard-detail', pk=1))
        self.assertEquals(response.status_code, 401)


class CreditCardTest(APITestCase):
    fixtures = ['patron', 'creditcard']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_credit_card_create(self):
        response = self.client.post(_location('creditcard-list'), {
            'expires': '0517',
            'holder_name': 'John Doe',
            'creditcard': '4987654321098769',
            'cvv': '123',
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('creditcard-detail', pk=response.data['id'])))

        CreditCard = get_model('accounts', 'CreditCard')
        card = CreditCard.objects.get(pk=response.data['id'])
        self.assertEqual(card.masked_number, '4XXXXXXXXXXXX769')
        self.assertEqual(card.expires, '0517')
        self.assertEqual(card.holder_name, 'John Doe')
        self.assertEqual(card.holder_id, 1)

    def test_credit_card_delete(self):
        CreditCard = get_model('accounts', 'CreditCard')
        self.assertEquals(CreditCard.objects.filter(pk=3).count(), 1)
        response = self.client.delete(_location('creditcard-detail', pk=3))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(CreditCard.objects.filter(pk=3).count(), 0)

    def test_credit_card_get_by_id(self):
        response = self.client.get(_location('creditcard-detail', pk=3))
        self.assertEquals(response.status_code, 200, response.data)

    def test_credit_card_list_paginated(self):
        response = self.client.get(_location('creditcard-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 1,
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))


class ProAgencyTest(APITestCase):

    fixtures = ['patron', 'proagency']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_pro_agency_create(self):
        response = self.client.post(_location('proagency-list'), {
            'name': 'Agency',
            'phone_number': '0198765432',
            'address': '2, rue debelleyme',
            'zipcode': '75003',
            'city': 'Paris',
            'country': 'FR',
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('proagency-detail', pk=response.data['id'])))

        ProAgency = get_model('accounts', 'ProAgency')
        agency = ProAgency.objects.get(pk=response.data['id'])

        self.assertEqual(agency.patron_id, 1)
        self.assertEqual(agency.name, 'Agency')
        self.assertEqual(agency.phone_number, '0198765432')
        self.assertEqual(agency.address1, '2, rue debelleyme')
        self.assertEqual(agency.zipcode, '75003')
        self.assertEqual(agency.city, 'Paris')
        self.assertEqual(agency.country, 'FR')

    def test_pro_agency_edit(self):
        response = self.client.patch(_location('proagency-detail', pk=1), {
            'city': 'Paris',
            'address': '2, rue debelleyme',
            'zipcode': '75003',
            'country': 'FR',
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)
        self.assertEquals(response.data['address'], '2, rue debelleyme')
        self.assertEquals(response.data['position']['coordinates'], [48.8603858, 2.3645553])

    def test_pro_agency_delete(self):
        ProAgency = get_model('accounts', 'ProAgency')
        self.assertEquals(ProAgency.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('proagency-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(ProAgency.objects.filter(pk=1).count(), 0)

    def test_pro_agency_get_by_id(self):
        response = self.client.get(_location('proagency-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_pro_agency_list_paginated(self):
        response = self.client.get(_location('proagency-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 2,
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))


class ProPackageTest(APITestCase):

    fixtures = ['patron', 'propackages']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_pro_package_create(self):
        response = self.client.post(_location('propackage-list'), {
            'name': 'Agency',
            'maximum_items': '10',
            'price': '1234',
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('propackage-detail', pk=response.data['id'])))

        ProPackage = get_model('accounts', 'ProPackage')
        package = ProPackage.objects.get(pk=response.data['id'])

        self.assertEqual(package.name, 'Agency')
        self.assertEqual(package.maximum_items, 10)
        self.assertEqual(package.price, Decimal(1234))
        self.assertEqual(package.valid_from, datetime.date.today())
        self.assertIsNone(package.valid_until)

    def test_pro_package_edit(self):
        response = self.client.patch(_location('propackage-detail', pk=1), {
            'valid_until': '2014-10-31',
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)

        ProPackage = get_model('accounts', 'ProPackage')
        package = ProPackage.objects.get(pk=response.data['id'])
        self.assertEqual(package.valid_until, datetime.date(2014, 10, 31))

    def test_pro_package_get_by_id(self):
        response = self.client.get(_location('propackage-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_pro_package_list_paginated(self):
        response = self.client.get(_location('propackage-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 5,
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))


class SubscriptionTest(APITestCase):

    fixtures = ['patron', 'propackages', 'subscriptions']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_subscription_create(self):
        response = self.client.post(_location('subscription-list'), {
            'propackage_id': _location('propackage-detail', pk=1),
            'payment_type': 'CHECK',
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('subscription-detail', pk=response.data['id'])))

        Subscription = get_model('accounts', 'Subscription')
        subscription = Subscription.objects.get(pk=response.data['id'])

        self.assertEqual(subscription.patron_id, 1)
        self.assertEqual(subscription.propackage_id, 1)
        self.assertEqual(subscription.payment_type, 1)
        self.assertEqual(subscription.subscription_started, datetime.date.today())
        self.assertIsNone(subscription.subscription_ended)

    def test_subscription_edit(self):
        response = self.client.put(_location('subscription-detail', pk=1), {
            'subscription_ended': '2014-10-31T00:00',
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)

        Subscription = get_model('accounts', 'Subscription')
        subscription = Subscription.objects.get(pk=response.data['id'])
        self.assertEqual(
            subscription.subscription_ended,
            datetime.datetime(2014, 10, 31))

    def test_subscription_get_by_id(self):
        response = self.client.get(_location('subscription-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_subscription_list_paginated(self):
        response = self.client.get(_location('subscription-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 1,
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))
