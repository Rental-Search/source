# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import get_model

from rest_framework.test import APITestCase

from rent.choices import COMMENT_TYPE_CHOICES

def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)

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