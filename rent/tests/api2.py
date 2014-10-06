# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db.models import get_model
from django.db import connection
from django.conf import settings

from rest_framework.test import APITestCase, APITransactionTestCase

from rent.choices import COMMENT_TYPE_CHOICES

def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)

class BookingTest(APITransactionTestCase):
    reset_sequences = True
    fixtures = ['patron', 'address', 'category', 'product', 'price', 'booking', 'comment', 'creditcard']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        connection.cursor().execute("select setval('rent_booking_contract_id_seq', %s);", [100])

    def test_booking_list(self):
        response = self.client.get(_location('booking-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 12,
            'previous': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(min(response.data['count'], settings.REST_FRAMEWORK['PAGINATE_BY']), len(response.data['results']))

    def test_booking_get_by_id(self):
        response = self.client.get(_location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 200, response.data)

    def test_booking_create(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=6),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('uuid', response.data)
        # the currently authenticated user must be used on creation
        self.assertTrue(response.data['borrower'].endswith(_location('patron-detail', pk=1)))
        # the owner must be taken from the product automatically
        self.assertTrue(response.data['owner'].endswith(_location('patron-detail', pk=4)))

        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('booking-detail', pk=response.data['uuid'])))

    def test_booking_create_borrower(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=6),
            'borrower': _location('patron-detail', pk=4),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # the currently authenticated user must be used on creation
        self.assertTrue(response.data['borrower'].endswith(_location('patron-detail', pk=1)))

    def test_booking_create_own_product_error(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=1),
        })
        self.assertEquals(response.status_code, 400, response.data)
#         self.assertIn('errors', response.data, response.data)
#         self.assertIn('product', response.data['errors'], response.data)

    def test_booking_comments(self):
        self.fail('Not implemented!')

    def test_booking_pay(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=6),
        })
        uuid = response.data['uuid']

        response = self.client.put(_location('booking-pay', uuid), {
            'expires': '0517',
            'holder_name': 'John Doe',
            'card_number': '4987654321098769',
            'cvv': '123',
        })
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

class CommentTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'booking', 'comment']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_comment_create_owner(self):
        response = self.client.post(_location('comment-list'), {
             'rate': 5,
             'comment': "J'ai pu poser mes questions avec des r\u00e9ponses rapides et pr\u00e9cises, propri\u00e9taire sympathique, je recommande",
             'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        Comment = get_model('rent', 'comment')
        c = Comment.objects.get(pk=response.data['id'])
        self.assertEquals(c.type, COMMENT_TYPE_CHOICES.OWNER)

    def test_comment_create_borrower(self):
        response = self.client.post(_location('comment-list'), {
             'rate': 5,
             'comment': "J'ai pu poser mes questions avec des r\u00e9ponses rapides et pr\u00e9cises, propri\u00e9taire sympathique, je recommande",
             'booking': _location('booking-detail', pk='8fd2f3df67e2488496899aeb22601b15'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        Comment = get_model('rent', 'comment')
        c = Comment.objects.get(pk=response.data['id'])
        self.assertEquals(c.type, COMMENT_TYPE_CHOICES.BORROWER)

    def test_comment_list(self):
        response = self.client.get(_location('comment-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 2, # we should get 2 comments
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))

    def test_comment_get_by_id(self):
        response = self.client.get(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_comment_get_author_owner(self):
        response = self.client.get(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('author', response.data, response.data)
        self.assertTrue(response.data['author'].endswith(_location('patron-detail', pk=2)))

    def test_comment_get_author_borrower(self):
        response = self.client.get(_location('comment-detail', pk=2))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('author', response.data, response.data)
        self.assertTrue(response.data['author'].endswith(_location('patron-detail', pk=1)))

    def test_comment_delete(self):
        Comment = get_model('rent', 'Comment')
        self.assertEquals(Comment.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(Comment.objects.filter(pk=1).count(), 0)


class SinisterTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'booking', 'sinister']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_sinister_create(self):
        response = self.client.post(_location('sinister-list'), {
            'product': _location('product-detail', pk=1),
            'patron': _location('patron-detail', pk=1),
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
            'description': 'Description'
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('uuid', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('sinister-detail', pk=response.data['uuid'])))

        Sinister = get_model('rent', 'Sinister')
        sinister = Sinister.objects.get(pk=response.data['uuid'])

        self.assertEqual(sinister.product_id, 1)
        self.assertEqual(sinister.patron_id, 1)
        self.assertEqual(sinister.booking_id, '87ee8e9dec1d47c29ebb27e09bda8fc3')
        self.assertEqual(sinister.description, 'Description')

    def test_sinister_get_by_id(self):
        response = self.client.get(_location('sinister-detail', pk='aaf26618b6654a05bf3cc57ade322928'))
        self.assertEquals(response.status_code, 200, response.data)

    def test_sinister_list_paginated(self):
        response = self.client.get(_location('sinister-list'))
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
