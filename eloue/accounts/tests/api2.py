# -*- coding: utf-8 -*-
import os.path
import base64

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
        response = self.client.get(_location('patron-list'), format='json')
        self.assertEquals(response.status_code, 401)

    def test_account_anonymous_creation_required(self):
        post_data = {
            'username': 'chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com',
        }
        response = self.client.post(_location('patron-list'), post_data, format='json')
        self.assertEquals(response.status_code, 201)

        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)

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
        res = self.client.post(_location('patron-list'), post_data, format='json')
        self.assertEquals(res.status_code, 201)

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
        self.assertEquals(response.status_code, 200)
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
            self.assertEquals(response.status_code, 200)
            self.assertTrue(User.objects.get(pk=1).avatar)

    def test_account_avatar_upload_json_base64(self):
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
            self.assertEquals(response.status_code, 200)
            self.assertTrue(User.objects.get(pk=1).avatar)

    def test_account_avatar_upload_json_url(self):
        self.assertFalse(User.objects.get(pk=1).avatar)
        response = self.client.put(_location('patron-detail', pk=1), {
            'avatar': {
                'content': 'http://liyaliao.weebly.com/uploads/1/5/2/9/15298970/6065967.jpg',
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(User.objects.get(pk=1).avatar)


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
