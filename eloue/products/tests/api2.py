# -*- coding: utf-8 -*-
import os.path
import base64

from django.db.models import get_model
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase

User = get_user_model()

IMAGE_FILE = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'bentley.jpg')
IMAGE_URL = 'http://www.topcarrating.com/jaguar/1966-jaguar-xj13.jpg'

def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)

class PictureTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'picture_api2']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_picture_create_multipart(self):
        with open(IMAGE_FILE, 'rb') as image:
            response = self.client.post(_location('picture-list'), {
                'product' : _location('product-detail', pk=1),
                'image': image,
            }, format='multipart')

            # check HTTP response code must be 201 CREATED
            self.assertEquals(response.status_code, 201, response.data)

            # Location header must be properly set to redirect to the resource have just been created
            self.assertIn('Location', response)
            self.assertTrue(response['Location'].endswith(_location('picture-detail', pk=response.data['id'])))

            # check returned attributes
            for k in ('id', 'created_at', 'image', 'product'):
                self.assertIn(k, response.data, response.data)
                self.assertTrue(response.data[k], response.data)

            # check processed images
            for k in ('thumbnail', 'profile', 'home', 'display'):
                self.assertIn(k, response.data['image'], response.data)
                self.assertTrue(response.data['image'][k], response.data)

            # check product has been applied properly
            self.assertTrue(response.data['product'].endswith(_location('product-detail', pk=1)))

    def test_picture_create_base64(self):
        with open(IMAGE_FILE, 'rb') as image:
            response = self.client.post(_location('picture-list'), {
                'product' : _location('product-detail', pk=1),
                'image': {
                    'content': base64.b64encode(image.read()),
                    'filename': os.path.basename(IMAGE_FILE),
                    #'encoding': 'base64',
                }
            })

            # check HTTP response code must be 201 CREATED
            self.assertEquals(response.status_code, 201, response.data)

            # Location header must be properly set to redirect to the resource have just been created
            self.assertIn('Location', response)
            self.assertTrue(response['Location'].endswith(_location('picture-detail', pk=response.data['id'])))

            # check returned attributes
            for k in ('id', 'created_at', 'image', 'product'):
                self.assertIn(k, response.data, response.data)
                self.assertTrue(response.data[k], response.data)

            # check processed images
            for k in ('thumbnail', 'profile', 'home', 'display'):
                self.assertIn(k, response.data['image'], response.data)
                self.assertTrue(response.data['image'][k], response.data)

            # check product has been applied properly
            self.assertTrue(response.data['product'].endswith(_location('product-detail', pk=1)))

    def test_picture_create_url(self):
        response = self.client.post(_location('picture-list'), {
            'product' : _location('product-detail', pk=1),
            'image': {
                'content': IMAGE_URL,
                'encoding': 'url',
            }
        })

        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('picture-detail', pk=response.data['id'])))

        # check returned attributes
        for k in ('id', 'created_at', 'image', 'product'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        # check processed images
        for k in ('thumbnail', 'profile', 'home', 'display'):
            self.assertIn(k, response.data['image'], response.data)
            self.assertTrue(response.data['image'][k], response.data)

        # check product has been applied properly
        self.assertTrue(response.data['product'].endswith(_location('product-detail', pk=1)))

    def test_picture_edit_multipart(self):
        with open(IMAGE_FILE, 'rb') as image:
            response = self.client.put(_location('picture-detail', pk=1), {
                'image': image,
            }, format='multipart')
            self.assertEquals(response.status_code, 200, response.data)

    def test_picture_edit_base64(self):
        with open(IMAGE_FILE, 'rb') as image:
            response = self.client.put(_location('picture-detail', pk=1), {
                'image': {
                    'content': base64.b64encode(image.read()),
                    'filename': os.path.basename(IMAGE_FILE),
                    #'encoding': 'base64',
                }
            })
            self.assertEquals(response.status_code, 200, response.data)

    def test_picture_edit_url(self):
        response = self.client.put(_location('picture-detail', pk=1), {
            'image': {
                'content': IMAGE_URL,
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 200, response.data)

    def test_picture_delete(self):
        Picture = get_model('products', 'Picture')
        self.assertEquals(Picture.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('picture-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(Picture.objects.filter(pk=1).count(), 0)

    def test_picture_list_paginated(self):
        response = self.client.get(_location('picture-list'))
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

    def test_picture_detail(self):
        response = self.client.get(_location('picture-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)
        # check retrieved resource detail format
        self.assertIn('product', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('image', response.data, response.data)
        for k in ('thumbnail', 'profile', 'home', 'display'):
            self.assertIn(k, response.data['image'], response.data)
            self.assertTrue(response.data['image'][k], response.data)

class MessageThreadTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'messagethread', 'message']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_messagethread_list_paginated(self):
        response = self.client.get(_location('messagethread-list'))
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

    def test_messagethread_create(self):
        response = self.client.post(_location('messagethread-list'), {
             'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=2),
             'subject': 'Test message thread',
        })

        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('messagethread-detail', pk=response.data['id'])))

        # check returned attributes
        for k in ('id', 'sender', 'recipient', 'subject'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

    def test_messagethread_create_fake_owner(self):
        response = self.client.post(_location('messagethread-list'), {
             'sender': _location('patron-detail', pk=2),
             'recipient': _location('patron-detail', pk=1),
             'subject': 'Fake owner message thread',
        })

        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # check that 'sender' has been overwritten in the back-end to refer to authenticated user
        self.assertTrue(response.data['sender'].endswith(_location('patron-detail', pk=1)), response.data)

class MessageTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'messagethread', 'message']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_message_list_paginated(self):
        response = self.client.get(_location('productrelatedmessage-list'))
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

    def test_message_create(self):
        response = self.client.post(_location('productrelatedmessage-list'), {
             'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=2),
             'thread': _location('messagethread-detail', pk=1),
             'body': 'Could you send me the contract again, please?',
        })

        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # check returned attributes
        for k in ('id', 'sender', 'recipient', 'sent_at', 'thread'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('productrelatedmessage-detail', pk=response.data['id'])))

    def test_message_create_fake_owner(self):
        response = self.client.post(_location('productrelatedmessage-list'), {
             'sender': _location('patron-detail', pk=2),
             'recipient': _location('patron-detail', pk=1),
             'thread': _location('messagethread-detail', pk=1),
             'body': 'Could you send me the contract again, please?',
        })

        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # check that 'sender' has been overwritten in the back-end to refer to authenticated user
        self.assertTrue(response.data['sender'].endswith(_location('patron-detail', pk=1)), response.data)

class MessageThreadMessageTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'messagethread', 'message', 'booking']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_message_create_with_offer(self):
        response = self.client.post(_location('messagethread-list'), {
             #'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=2),
             'subject': 'Test message thread (offer)',
             'product': _location('product-detail', pk=5),
        })
        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # check that 'sender' has been set in the back-end to refer to authenticated user
        self.assertTrue(response.data['sender'].endswith(_location('patron-detail', pk=1)), response.data)

        thread_id = response.data['id']

        response = self.client.post(_location('productrelatedmessage-list'), {
             #'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=2),
             'thread': _location('messagethread-detail', pk=thread_id),
             'offer': _location('booking-detail', pk='1661f5f6f9e14b43813b3c1913a7c26d'),
             'subject': 'Test message (offer)',
             'body': 'Please consider my offer.',
        })

        # check that 'sender' has been set in the back-end to refer to authenticated user
        self.assertTrue(response.data['sender'].endswith(_location('patron-detail', pk=1)), response.data)

        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # check returned attributes
        for k in ('id', 'sender', 'recipient', 'sent_at', 'thread'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        message_id = response.data['id']

        # check thread's 'last_messaage' has been updated
        response = self.client.get(_location('messagethread-detail', pk=thread_id))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertTrue(str(response.data['last_message']).endswith(_location('productrelatedmessage-detail', pk=message_id)), response.data)

        if 'last_offer' in response.data:
            self.assertTrue(str(response.data['last_offer']).endswith(_location('productrelatedmessage-detail', pk=message_id)), response.data)

class ProductTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'picture_api2']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_edit_address(self):
        response = self.client.get(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)
        self.assertEquals(response.data['id'], 1)
        product_id = response.data['id']

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
        response = self.client.patch(_location('product-detail', pk=product_id), {
            'address': _location('address-detail', pk=address_id),
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('address', response.data, response.data)
        self.assertTrue(len(response.data['address']), response.data['address'])
        self.assertEquals(response.data['address']['id'], address_id, response.data)

    def test_edit_phone(self):
        response = self.client.get(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)
        self.assertEquals(response.data['id'], 1)
        product_id = response.data['id']

        # create a new PhoneNumber record
        response = self.client.post(_location('phonenumber-list'), {
            'number': '0198765432',
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('id', response.data)
        phonenumber_id = response.data['id']

        # set the PhoneNumber record we've just created as the 'default_number' attribute
        response = self.client.patch(_location('product-detail', pk=product_id), {
            'phone': _location('phonenumber-detail', pk=phonenumber_id),
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('phone', response.data, response.data)
        self.assertTrue(len(response.data['phone']), response.data['phone'])
        self.assertEquals(response.data['phone']['id'], phonenumber_id, response.data)
