# -*- coding: utf-8 -*-
from operator import itemgetter
import os.path
import base64
from datetime import date
from decimal import Decimal
import datetime
import logging

from django.db.models import get_model
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase

User = get_user_model()

IMAGE_FILE = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'bentley.jpg')
IMAGE_URL = 'http://www.topcarrating.com/jaguar/1966-jaguar-xj13.jpg'

logging.getLogger('elasticsearch').setLevel(logging.ERROR)


def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)


class AnonymousPictureTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'picture_api2']
    public_fields = ('product', 'created_at', 'image')
    private_fields = tuple()

    def test_picture_list_forbidden(self):
        response = self.client.get(_location('picture-list'))
        self.assertEquals(response.status_code, 401)

    def test_picture_show_allowed(self):
        response = self.client.get(_location('picture-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_picture_create_forbidden(self):
        response = self.client.post(_location('picture-list'))
        self.assertEquals(response.status_code, 401)

    def test_picture_update_forbidden(self):
        response = self.client.put(_location('picture-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_picture_delete_forbidden(self):
        response = self.client.delete(_location('picture-detail', pk=1))
        self.assertEquals(response.status_code, 401)


class PictureTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'picture_api2']

    def setUp(self):
        self.model = get_model('products', 'Picture')
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
            'product': _location('product-detail', pk=1),
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

    def test_picture_create_url_wrong_url(self):
        response = self.client.post(_location('picture-list'), {
            'product': _location('product-detail', pk=1),
            'image': {
                'content': 'wrong_url',
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('image', response.data['errors'])

    def test_picture_create_url_not_exist_url(self):
        response = self.client.post(_location('picture-list'), {
            'product': _location('product-detail', pk=1),
            'image': {
                'content': IMAGE_URL.replace('.jpg', '.png'),
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('image', response.data['errors'])

    def test_picture_create_not_mine_product(self):
        response = self.client.post(_location('picture-list'), {
            'product': _location('product-detail', pk=6),
            'image': {
                'content': IMAGE_URL,
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 400, response.data)

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

    def test_picture_edit_not_mine_product(self):
        response = self.client.patch(_location('picture-detail', pk=2), {
            'image': {
                'content': IMAGE_URL,
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 404, response.data)

    def test_picture_delete(self):
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('picture-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(self.model.objects.filter(pk=1).count(), 0)

    def test_picture_delete_not_mine_product(self):
        self.assertEquals(self.model.objects.filter(pk=2).count(), 1)
        response = self.client.delete(_location('picture-detail', pk=2))
        self.assertEquals(response.status_code, 404, response.data)
        self.assertEquals(self.model.objects.filter(pk=2).count(), 1)

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

    def test_ordering(self):
        response = self.client.get(_location('picture-list'), {'ordering': 'created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'], sorted(response.data['results'], key=itemgetter('created_at')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('picture-list'), {'ordering': '-created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('created_at'), reverse=True))


class StaffPictureTest(APITestCase):
    fixtures = ['patron_staff', 'address', 'category', 'product', 'picture_api2']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_ordering(self):
        response = self.client.get(_location('picture-list'), {'ordering': 'created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'], sorted(response.data['results'], key=itemgetter('created_at')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('picture-list'), {'ordering': '-created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('created_at'), reverse=True))


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

    def test_not_empty_messagethread_list_paginated(self):
        response = self.client.get(
                _location('messagethread-list'), {'empty': False})
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
        self.assertEqual(response.data['sender']['id'], 1)

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

#    def test_message_edit(self):
#        response = self.client.patch(_location('productrelatedmessage-detail', 1), {
#            'read_at': '2014-10-14T00:00',
#        })
#        self.assertEquals(response.status_code, 200, response.data)

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
        self.assertEqual(response.data['sender']['id'], 1)

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
        self.assertEqual(response.data['last_message']['id'], message_id)
        if 'last_offer' in response.data:
            self.assertTrue(str(response.data['last_offer']).endswith(_location('productrelatedmessage-detail', pk=message_id)), response.data)

    def test_message_read_at(self):
        response = self.client.post(_location('messagethread-list'), {
             #'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=2),
             'subject': 'Test message thread (offer)',
             'product': _location('product-detail', pk=5),
        })
        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)

        # check that 'sender' has been set in the back-end to refer to authenticated user
        self.assertEqual(response.data['sender']['id'], 1)

        thread_id = response.data['id']

        response = self.client.post(_location('productrelatedmessage-list'), {
             #'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=2),
             'thread': _location('messagethread-detail', pk=thread_id),
             'subject': 'Test message (offer)',
             'body': 'Please consider my offer.',
        })
        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)
        message_id = response.data['id']

        # check 'read_at' has been set
        self.client.logout()
        self.client.login(username='timothee.peignier@e-loue.com', password='timothee')

        response = self.client.get(_location(
            'productrelatedmessage-seen', pk=message_id))
        self.assertEquals(response.status_code, 204, response.data)

        # create answer
        response = self.client.post(_location('productrelatedmessage-list'), {
             #'sender': _location('patron-detail', pk=1),
             'recipient': _location('patron-detail', pk=1),
             'thread': _location('messagethread-detail', pk=thread_id),
             'subject': 'Test answer',
             'body': 'Check reat at time',
        })
        # check HTTP response code must be 201 CREATED
        self.assertEquals(response.status_code, 201, response.data)
        message_id = response.data['id']

        self.client.logout()
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

        response = self.client.get(_location(
            'productrelatedmessage-seen', pk=message_id))
        self.assertEquals(response.status_code, 204, response.data)


class AnonymousProductTest(APITestCase):

    fixtures = ['patron', 'address', 'phones', 'category', 'product', 'price', 'picture_api2']

    public_fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'quantity', 'category',
                     'owner', 'pro_agencies', 'comment_count', 'average_note')
    private_fields = ('is_archived', 'created_at',)

    def test_product_list_allowed(self):
        response = self.client.get(_location('product-list'))
        self.assertEquals(response.status_code, 401)

    def test_product_search_allowed(self):
        response = self.client.get(_location('product-list'), {
            'quantity': 3,
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        data = response.data['results'][0]

        for field in self.public_fields:
            self.assertIn(field, data, field)

        for field in self.private_fields:
            self.assertNotIn(field, data, field)

    def test_product_show_allowed(self):
        response = self.client.get(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_product_update_forbidden(self):
        response = self.client.put(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_product_delete_forbidden(self):
        response = self.client.delete(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_product_create_forbidden(self):
        response = self.client.post(_location('product-list'))
        self.assertEquals(response.status_code, 401)

    def test_product_is_available_allowed(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)
        response = self.client.get(_location('product-is-available', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('max_available', response.data)
        self.assertEqual(response.data['max_available'], 3)

    def test_homepage_allowed(self):
        response = self.client.get(_location('product-homepage'))
        self.assertEquals(response.status_code, 200)

    def test_unavailability_periods_allowed(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)

        response = self.client.get(_location('product-unavailability-periods', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 0)

class ProductTest(APITestCase):
    fixtures = ['patron', 'address', 'phones', 'category', 'product', 'price', 'picture_api2']

    def setUp(self):
        self.model = get_model('products', 'Product')
        self.car_model = get_model('products', 'CarProduct')
        self.real_estate_model = get_model('products', 'RealEstateProduct')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        self.borrower_model = get_model('accounts', 'Patron')

    def test_is_product_available(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)
        response = self.client.get(_location('product-is-available', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('max_available', response.data)
        self.assertEqual(response.data['max_available'], 3)

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

    def test_product_get_by_id(self):
        response = self.client.get(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_product_list_paginated(self):
        response = self.client.get(_location('product-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 6,
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))

    def test_product_create(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=1),
            'summary': 'test summary',
            'description': 'test description',
            'address': _location('address-detail', pk=1),
            'phone': _location('phonenumber-detail', pk=1),
            'deposit_amount': 150,
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('product-detail', pk=response.data['id'])))
        self.assertTrue(self.model.objects.filter(pk=response.data['id']).exists())

    def test_product_create_not_mine(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=1),
            'summary': 'test summary',
            'description': 'test description',
            'address': _location('address-detail', pk=1),
            'phone': _location('phonenumber-detail', pk=1),
            'deposit_amount': 150,
            'owner': _location('patron-detail', pk=2)
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('product-detail', pk=response.data['id'])))
        # End user can't create record for other person. Owner is force set as current user.
        product = self.model.objects.get(pk=response.data['id'])
        self.assertEqual(product.owner_id, 1)
        self.assertEqual(response.data['owner']['id'], 1)
        self.assertTrue(self.model.objects.filter(pk=response.data['id']).exists())

    def test_product_create_negative_amount(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=1),
            'summary': 'test summary',
            'description': 'test description',
            'address': _location('address-detail', pk=1),
            'phone': _location('phonenumber-detail', pk=1),
            'deposit_amount': -1,
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('deposit_amount', response.data['errors'], response.data)

    def test_product_create_large_amount(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=1),
            'summary': 'test summary',
            'description': 'test description',
            'address': _location('address-detail', pk=1),
            'phone': _location('phonenumber-detail', pk=1),
            'deposit_amount': 12345678912,
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('deposit_amount', response.data['errors'], response.data)

    def test_product_create_no_fields(self):
        response = self.client.post(_location('product-list'))
        self.assertEquals(response.status_code, 400, response.data)

        required_fields = {'summary', 'address', 'category', 'owner', 'deposit_amount', }
        default_fields = {'owner'}
        for field in required_fields - default_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_product_create_car_required_fields(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=477),
            'summary': 'test car summary',
            'address': _location('address-detail', pk=1),
            'deposit_amount': 600,

            'brand': 'Toyota',
            'model': 'FunCargo',
            'km_included': 1000,

            'tax_horsepower': 1,
            'first_registration_date': '2010-01-01',
            'licence_plate': '123456'

        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('product-detail', pk=response.data['id'])))
        self.assertTrue(self.car_model.objects.filter(pk=response.data['id']).exists())

    def test_product_create_car(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=477),
            'summary': 'test car summary',
            'description': 'test car description',
            'address': _location('address-detail', pk=1),
            'phone': _location('phonenumber-detail', pk=1),
            'deposit_amount': 600,

            'brand': 'Toyota',
            'model': 'FunCargo',

            # options & accessoires
            'air_conditioning': True,
            'power_steering': True,
            'cruise_control': True,
            'gps': False,
            'baby_seat': True,
            'roof_box': False,
            'bike_rack': False,
            'snow_tires': True,
            'snow_chains': False,
            'ski_rack': False,
            'cd_player': True,
            'audio_input': False,

            # informations de l'assurance
            'tax_horsepower': 9,
            'licence_plate': 'TX 234563',
            'first_registration_date': date(2003, 11, 05),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('product-detail', pk=response.data['id'])))
        self.assertTrue(self.car_model.objects.filter(pk=response.data['id']).exists())

    def test_product_create_real_estate_required_fields(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=385),
            'summary': 'test maison summary',
            'address': _location('address-detail', pk=1),
            'deposit_amount': 100,

            'capacity': 6,
            'private_life': 1,
            'chamber_number': 3,
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('product-detail', pk=response.data['id'])))
        self.assertTrue(self.real_estate_model.objects.filter(pk=response.data['id']).exists())

    def test_product_create_real_estate(self):
        response = self.client.post(_location('product-list'), {
            'category': _location('category-detail', pk=385),
            'summary': 'test maison summary',
            'description': 'test maison description',
            'address': _location('address-detail', pk=1),
            'phone': _location('phonenumber-detail', pk=1),
            'deposit_amount': 100,

            'capacity': 6,
            'private_life': 1,
            'chamber_number': 3,

            # service_included
            'air_conditioning': False,
            'breakfast': False,
            'balcony': True,
            'lockable_chamber': True,
            'towel': True,
            'lift': False,
            'family_friendly': False,
            'gym': False,
            'accessible': True,
            'heating': True,
            'jacuzzi': False,
            'chimney': False,
            'internet_access': True,
            'kitchen': True,
            'parking': False,
            'smoking_accepted': False,
            'ideal_for_events': False,
            'tv': True,
            'washing_machine': True,
            'tumble_dryer': True,
            'computer_with_internet': True,
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('product-detail', pk=response.data['id'])))
        self.assertTrue(self.real_estate_model.objects.filter(pk=response.data['id']).exists())

    def test_product_delete(self):
        self.assertEquals(self.model.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('product-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(self.model.objects.filter(pk=1).count(), 0)

    def test_product_delete_not_mine(self):
        self.assertEquals(self.model.objects.filter(pk=6).count(), 1)
        response = self.client.delete(_location('product-detail', pk=6))
        # FIXME: should be 404 for accordance with other api behaviour
        self.assertEquals(response.status_code, 403, response.data)
        self.assertEquals(self.model.objects.filter(pk=6).count(), 1)

    def test_ordering(self):
        response = self.client.get(_location('product-list'), {'ordering': 'quantity'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'], sorted(response.data['results'], key=itemgetter('quantity')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('product-list'), {'ordering': '-quantity'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('quantity'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('product-list'), {'deposit_amount': 250})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['deposit_amount'] == 250, response.data['results']))
        self.assertEqual([], filter(lambda x: x['deposit_amount'] != 250, response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('product-list'), {'deposit_amount': 700})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['deposit_amount'] == 700, response.data['results']))
        self.assertEqual([], filter(lambda x: x['deposit_amount'] != 700, response.data['results']))

    # For test searching index we have to generate index for test data (maybe mock?)
    def test_filter_prices(self):
        response = self.client.get(_location('product-list'), {'price_from': 10, 'price_to': 20})
        self.assertEquals(response.status_code, 200, response.data)
        #self.assertGreater(response.data['count'], 0)

    def test_filter_q(self):
        response = self.client.get(_location('product-list'), {'q': 'Philips'})
        self.assertEquals(response.status_code, 200, response.data)
        #self.assertGreater(response.data['count'], 0)

    def test_filter_q_and_ordering(self):
        response = self.client.get(_location('product-list'), {
            'q': 'Philips', 'ordering': '-average_rate'})
        self.assertEquals(response.status_code, 200, response.data)

    def test_homepage_allowed(self):
        response = self.client.get(_location('product-homepage'))
        self.assertEquals(response.status_code, 200)

    def test_unavailability_periods_before_now(self):
        start_date = datetime.datetime.today() - datetime.timedelta(days=2)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)

        response = self.client.get(_location('product-unavailability-periods', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)

    def test_unavailability_periods_wrong_date(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=2)
        end_date = datetime.datetime.today() - datetime.timedelta(days=2)

        response = self.client.get(_location('product-unavailability-periods', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 400, response.data)

    def test_empty_unavailability_periods(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)

        response = self.client.get(_location('product-unavailability-periods', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['results']), 0)

    def test_unavailability_periods(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)

        product = self.model.objects.get(pk=7)
        unavailable = product.unavailabilityperiod_set.create(
                started_at=start_date,
                ended_at=end_date,
                quantity=1)

        response = self.client.get(_location('product-unavailability-periods', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['results']), 1)
        period = response.data['results'][0]
        self.assertEqual(period['started_at'], start_date)
        self.assertEqual(period['ended_at'], end_date)
        self.assertEqual(period['quantity'], 1)
        self.assertEqual(period['id'], unavailable.pk)
        self.assertTrue(period['product'].endswith(
            _location('product-detail', pk=7)))

    def test_unavailability_and_booking_periods(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)

        product = self.model.objects.get(pk=7)
        unavailable = product.unavailabilityperiod_set.create(
                started_at=start_date,
                ended_at=end_date,
                quantity=1)

        booking = product.bookings.create(
                uuid= '87ee8e9dec1d47c29ebb27e09bda8fc8',
                started_at=start_date,
                ended_at=end_date + datetime.timedelta(days=2),
                quantity=1,
                state='pending',
                deposit_amount=100,
                insurance_amount=10,
                total_amount=10,
                currency='EUR',
                owner=product.owner,
                borrower=self.borrower_model.objects.get(pk=2),
                contract_id=678,
                pin='qqq',
                created_at=start_date - datetime.timedelta(days=1),
                )

        response = self.client.get(_location('product-unavailability-periods', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['results']), 2)

        period = response.data['results'][0]
        self.assertEqual(period['started_at'], start_date)
        self.assertEqual(period['ended_at'], end_date + datetime.timedelta(days=2))
        self.assertEqual(period['quantity'], 1)
        self.assertIsNone(period['id'])

        period = response.data['results'][1]
        self.assertEqual(period['started_at'], start_date)
        self.assertEqual(period['ended_at'], end_date)
        self.assertEqual(period['quantity'], 1)
        self.assertEqual(period['id'], unavailable.pk)
        self.assertTrue(period['product'].endswith(
            _location('product-detail', pk=7)))

    def test_unavailability(self):
        start_date = datetime.datetime.today() + datetime.timedelta(days=1)
        end_date = datetime.datetime.today() + datetime.timedelta(days=2)

        product = self.model.objects.get(pk=7)
        unavailable = product.unavailabilityperiod_set.create(
                started_at=start_date,
                ended_at=end_date,
                quantity=1)

        booking = product.bookings.create(
                uuid= '87ee8e9dec1d47c29ebb27e09bda8fc8',
                started_at=start_date,
                ended_at=end_date + datetime.timedelta(days=2),
                quantity=1,
                state='pending',
                deposit_amount=100,
                insurance_amount=10,
                total_amount=10,
                currency='EUR',
                owner=product.owner,
                borrower=self.borrower_model.objects.get(pk=2),
                contract_id=678,
                pin='qqq',
                created_at=start_date - datetime.timedelta(days=1),
                )

        response = self.client.get(_location('product-unavailability', pk=7), {
            'started_at': start_date.strftime('%d/%m/%Y %H:%M'),
            'ended_at': end_date.strftime('%d/%m/%Y %H:%M'),
            'quantity': 2
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('unavailable_periods', response.data)
        self.assertEqual(len(response.data['unavailable_periods']), 1)
        self.assertEqual(response.data['unavailable_periods'][0], {
            'id': unavailable.pk,
            'started_at': start_date,
            'ended_at': end_date,
            'quantity': 1,
        })

        self.assertIn('booking_periods', response.data)
        self.assertEqual(len(response.data['booking_periods']), 1)
        period = response.data['booking_periods'][0]
        self.assertEqual(period['started_at'], start_date)
        self.assertEqual(period['ended_at'],
                end_date + datetime.timedelta(days=2))
        self.assertEqual(period['quantity'], 1)

class StaffProductTest(APITestCase):
    fixtures = ['patron_staff', 'address', 'phones', 'category', 'product', 'price', 'picture_api2']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_ordering(self):
        response = self.client.get(_location('product-list'), {'ordering': 'quantity'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'], sorted(response.data['results'], key=itemgetter('quantity')))

    def test_ordering_private_field(self):
        response = self.client.get(_location('product-list'), {'ordering': 'is_archived'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'], sorted(response.data['results'], key=itemgetter('is_archived')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('product-list'), {'ordering': '-quantity'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('quantity'), reverse=True))

    def test_filter_private_field1(self):
        response = self.client.get(_location('product-list'), {'is_archived': True})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['count'], 0)

    def test_filter_private_field2(self):
        response = self.client.get(_location('product-list'), {'is_archived': False})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: not x['is_archived'], response.data['results']))
        self.assertEqual([], filter(lambda x: x['is_archived'], response.data['results']))

    def test_filter1(self):
        response = self.client.get(_location('product-list'), {'deposit_amount': 250})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['deposit_amount'] == 250, response.data['results']))
        self.assertEqual([], filter(lambda x: x['deposit_amount'] != 250, response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('product-list'), {'deposit_amount': 700})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['deposit_amount'] == 700, response.data['results']))
        self.assertEqual([], filter(lambda x: x['deposit_amount'] != 700, response.data['results']))


class AnonymousCategoryTest(APITestCase):

    fixtures = ['patron', 'category']
    public_fields = ('parent', 'name', 'need_insurance', 'title', 'description', 'header', 'footer', 'is_child_node',
                     'is_leaf_node', 'is_root_node',)
    private_fields = tuple()

    def test_category_list_allowed(self):
        response = self.client.get(_location('category-list'))
        self.assertEquals(response.status_code, 200)
        expected = {
            'count': 26,
            'previous': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)

        self.assertEquals(len(response.data['results']), 10)
        for field in self.public_fields:
            self.assertIn(field, response.data['results'][0], field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data['results'][0], field)

    def test_category_show_allowed(self):
        response = self.client.get(_location('category-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_category_create_forbidden(self):
        response = self.client.post(_location('category-list'))
        self.assertEquals(response.status_code, 401)

    def test_category_update_forbidden(self):
        response = self.client.put(_location('category-detail', pk=1))
        self.assertEquals(response.status_code, 401)

    def test_category_get_ancestor_allowed(self):
        response = self.client.get(_location('category-ancestors', pk=475))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)
        self.assertIn('id', response.data[0])
        self.assertEqual(response.data[0]['id'], 3)

        for field in self.public_fields:
            self.assertIn(field, response.data[0], field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data[0], field)

    def test_category_get_children_allowed(self):
        response = self.client.get(_location('category-children', pk=3))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)
        self.assertIn('id', response.data[0])
        self.assertEqual(response.data[0]['id'], 475)

        for field in self.public_fields:
            self.assertIn(field, response.data[0], field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data[0], field)

    def test_category_get_descendants_allowed(self):
        response = self.client.get(_location('category-descendants', pk=3))
        descendants_ids = [475, 476, 477, 665]
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 4)
        for descendant in response.data:
            self.assertIn('id', descendant)
            self.assertIn(descendant['id'], descendants_ids)

        for field in self.public_fields:
            self.assertIn(field, response.data[0], field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data[0], field)


class CategoryTest(APITestCase):
    fixtures = ['patron', 'category']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_category_create(self):
        response = self.client.post(_location('category-list'), {
            'name': 'Test',
            'need_insurance': False,
        })

        self.assertEquals(response.status_code, 403, response.data)

    def test_category_edit(self):
        response = self.client.patch(_location('category-detail', pk=1), {
            'title': 'Title',
            'description': 'Description',
        })
        self.assertEquals(response.status_code, 403, response.data)

    def test_category_get_ancestor(self):
        response = self.client.get(_location('category-ancestors', pk=475))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)
        self.assertIn('id', response.data[0])
        self.assertEqual(response.data[0]['id'], 3)

    def test_category_get_children(self):
        response = self.client.get(_location('category-children', pk=3))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)
        self.assertIn('id', response.data[0])
        self.assertEqual(response.data[0]['id'], 475)

    def test_category_get_descendants(self):
        response = self.client.get(_location('category-descendants', pk=3))
        descendants_ids = [475, 476, 477, 665]
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 4)
        for descendant in response.data:
            self.assertIn('id', descendant)
            self.assertIn(descendant['id'], descendants_ids)

    def test_category_get_by_id(self):
        response = self.client.get(_location('category-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_category_list_paginated(self):
        response = self.client.get(_location('category-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 26,
            'previous': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertTrue(response.data['next'].endswith(_location('category-list') + '?page=2'))
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(len(response.data['results']), 10)

    def test_ordering(self):
        response = self.client.get(_location('category-list'), {'ordering': 'name'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'], sorted(response.data['results'], key=itemgetter('name')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('category-list'), {'ordering': '-name'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('name'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('category-list'), {'is_child_node': True})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['is_child_node'], response.data['results']))
        self.assertEqual([], filter(lambda x: not x['is_child_node'], response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('category-list'), {'is_child_node': False})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: not x['is_child_node'], response.data['results']))
        self.assertEqual([], filter(lambda x: x['is_child_node'], response.data['results']))


class StaffCategoryTest(APITestCase):
    fixtures = ['patron_staff', 'category']

    def setUp(self):
        user = get_user_model().objects.get(pk=1)
        permissions = get_model('auth', 'Permission').objects.filter(codename__contains='category')
        for permission in permissions:
            user.user_permissions.add(permission)
        user.save()
        self.model = get_model('products', 'Category')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_category_create(self):
        response = self.client.post(_location('category-list'), {
            'name': 'Test',
            'need_insurance': False,
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('category-detail', pk=response.data['id'])))

        category = self.model.objects.get(pk=response.data['id'])
        self.assertEqual(category.name, 'Test')
        self.assertFalse(category.need_insurance)
        self.assertIsNone(category.parent_id)
        self.assertEqual(category.lft, 1)
        self.assertEqual(category.rght, 2)
        self.assertEqual(category.level, 0)

    def test_category_edit(self):
        response = self.client.patch(_location('category-detail', pk=1), {
            'title': 'Title',
            'description': 'Description',
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)

        category = self.model.objects.get(pk=response.data['id'])
        self.assertEquals(category.title, 'Title')
        self.assertEquals(category.description, 'Description')

    def test_ordering(self):
        response = self.client.get(_location('category-list'), {'ordering': 'name'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('name')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('category-list'), {'ordering': '-name'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('name'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('category-list'), {'is_child_node': True})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['is_child_node'], response.data['results']))
        self.assertEqual([], filter(lambda x: not x['is_child_node'], response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('category-list'), {'is_child_node': False})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: not x['is_child_node'], response.data['results']))
        self.assertEqual([], filter(lambda x: x['is_child_node'], response.data['results']))


class AnonymousPriceTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'price']
    public_fields = ('name', 'amount', 'product', 'unit', 'currency')
    private_fields = tuple()

    def test_price_list_forbidden(self):
        response = self.client.get(_location('price-list'))
        self.assertEquals(response.status_code, 401)

    def test_price_show_allowed(self):
        response = self.client.get(_location('price-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_price_create_forbidden(self):
        response = self.client.post(_location('price-list'))
        self.assertEquals(response.status_code, 401)

    def test_price_update_forbidden(self):
        response = self.client.put(_location('price-detail', pk=1))
        self.assertEquals(response.status_code, 401)


class PriceTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'price']

    def setUp(self):
        self.model = get_model('products', 'Price')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_price_create_not_mine_product(self):
        response = self.client.post(_location('price-list'), {
            'product': _location('product-detail', pk=6),
            'amount': 10,
            'unit': 0,
            'currency': 'EUR'
        })

        self.assertEquals(response.status_code, 400, response.data)

    def test_price_create_negative_amount(self):
        response = self.client.post(_location('price-list'), {
            'product': _location('product-detail', pk=1),
            'amount': -10,
            'unit': 0,
            'currency': 'EUR'
        })

        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('amount', response.data['errors'], response.data)

    def test_price_create_large_amount(self):
        response = self.client.post(_location('price-list'), {
            'product': _location('product-detail', pk=1),
            'amount': 12345678912,
            'unit': 0,
            'currency': 'EUR'
        })

        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('amount', response.data['errors'], response.data)

    def test_price_create_no_fields(self):
        response = self.client.post(_location('price-list'))
        self.assertEquals(response.status_code, 400, response.data)

        required_fields = {'amount', 'product', 'unit', }
        default_fields = set()
        for field in required_fields - default_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_price_create(self):
        response = self.client.post(_location('price-list'), {
            'product': _location('product-detail', pk=1),
            'amount': 10,
            'unit': 0,
            'currency': 'EUR'
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('price-detail', pk=response.data['id'])))

        Price = get_model('products', 'Price')
        price = Price.objects.get(pk=response.data['id'])

        self.assertEqual(price.amount, Decimal(10))
        self.assertEqual(price.currency, 'EUR')
        self.assertEqual(price.product_id, 1)
        self.assertEqual(price.unit, 0)

    def test_price_edit(self):
        response = self.client.patch(_location('price-detail', pk=1), {
            'name': 'Name',
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)

        Price = get_model('products', 'Price')
        price = Price.objects.get(pk=response.data['id'])
        self.assertEqual(price.name, 'Name')

    def test_price_edit_not_mine_product(self):
        response = self.client.patch(_location('price-detail', pk=14), {
            'name': 'Name',
        })
        self.assertEquals(response.status_code, 404, response.data)

    def test_price_edit_negative_amount(self):
        response = self.client.patch(_location('price-detail', pk=1), {
            'amount': -10,
        })

        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('amount', response.data['errors'], response.data)

    def test_price_edit_large_amount(self):
        response = self.client.patch(_location('price-detail', pk=1), {
            'amount': 12345678912,
        })

        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('amount', response.data['errors'], response.data)

    def test_price_get_by_id(self):
        response = self.client.get(_location('price-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_price_list_paginated(self):
        response = self.client.get(_location('price-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 15,
            'previous': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertTrue(response.data['next'].endswith(_location('price-list') + '?page=2'))
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(len(response.data['results']), 10)

    def test_ordering(self):
        response = self.client.get(_location('price-list'), {'ordering': 'amount'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('amount')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('price-list'), {'ordering': '-amount'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('amount'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('price-list'), {'product': 1})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(
            response.data['results'],
            filter(lambda x: x['product'].endswith(_location('product-detail', pk=1)), response.data['results']))
        self.assertEqual(
            [],
            filter(lambda x: not x['product'].endswith(_location('product-detail', pk=1)), response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('price-list'), {'product': 2})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(
            response.data['results'],
            filter(lambda x: x['product'].endswith(_location('product-detail', pk=2)), response.data['results']))
        self.assertEqual(
            [],
            filter(lambda x: not x['product'].endswith(_location('product-detail', pk=2)), response.data['results']))


class StaffPriceTest(APITestCase):
    fixtures = ['patron_staff', 'address', 'category', 'product', 'price']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_ordering(self):
        response = self.client.get(_location('price-list'), {'ordering': 'amount'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('amount')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('price-list'), {'ordering': '-amount'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('amount'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('price-list'), {'product': 1})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(
            response.data['results'],
            filter(lambda x: x['product'].endswith(_location('product-detail', pk=1)), response.data['results']))
        self.assertEqual(
            [],
            filter(lambda x: not x['product'].endswith(_location('product-detail', pk=1)), response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('price-list'), {'product': 2})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(
            response.data['results'],
            filter(lambda x: x['product'].endswith(_location('product-detail', pk=2)), response.data['results']))
        self.assertEqual(
            [],
            filter(lambda x: not x['product'].endswith(_location('product-detail', pk=2)), response.data['results']))


class AnonymousCuriosityTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'curiosity']
    public_fields = ('product', )
    private_fields = tuple()

    def test_curiosity_list_allowed(self):
        response = self.client.get(_location('curiosity-list'))
        self.assertEquals(response.status_code, 200)
        expected = {
            'count': 2,
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)

        self.assertEquals(response.data['count'], len(response.data['results']))
        for field in self.public_fields:
            self.assertIn(field, response.data['results'][0], field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data['results'][0], field)

    def test_curiosity_show_allowed(self):
        response = self.client.get(_location('curiosity-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_curiosity_create_forbidden(self):
        response = self.client.post(_location('curiosity-list'))
        self.assertEquals(response.status_code, 401)

    def test_curiosity_update_forbidden(self):
        response = self.client.put(_location('curiosity-detail', pk=1))
        self.assertEquals(response.status_code, 401)


class CuriosityTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'curiosity']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_curiosity_create(self):
        response = self.client.post(_location('curiosity-list'), {
            'product': _location('product-detail', pk=1),
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('id', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('curiosity-detail', pk=response.data['id'])))

        Curiosity = get_model('products', 'Curiosity')
        curiosity = Curiosity.objects.get(pk=response.data['id'])

        self.assertEqual(curiosity.product_id, 1)

    def test_curiosity_immutable(self):
        response = self.client.patch(_location('curiosity-detail', pk=1), {
            'product': _location('product-detail', pk=2),
        })
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('id', response.data)

        Curiosity = get_model('products', 'Curiosity')
        curiosity = Curiosity.objects.get(pk=response.data['id'])
        self.assertEqual(curiosity.product_id, 1)

    def test_curiosity_get_by_id(self):
        response = self.client.get(_location('curiosity-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_price_list_paginated(self):
        response = self.client.get(_location('curiosity-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 2,
            'previous': None,
            'next': None
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))
