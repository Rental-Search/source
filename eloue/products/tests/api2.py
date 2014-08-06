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
    fixtures = ['patron', 'address', 'category', 'product', 'picture']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_picture_create_multipart(self):
        with open(IMAGE_FILE, 'rb') as image:
            response = self.client.post(_location('picture-list'), {
                'product' : _location('product-detail', pk=1),
                'image': image,
            }, format='multipart')
            self.assertEquals(response.status_code, 201, response.data)
            self.assertIn('created_at', response.data)
            self.assertIn('image', response.data, response.data)
            for k in ('thumbnail', 'profile', 'home', 'display'):
                self.assertIn(k, response.data['image'], response.data)
                self.assertTrue(response.data['image'][k], response.data)

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
            self.assertEquals(response.status_code, 201, response.data)
            self.assertIn('created_at', response.data)
            self.assertIn('image', response.data, response.data)
            for k in ('thumbnail', 'profile', 'home', 'display'):
                self.assertIn(k, response.data['image'], response.data)
                self.assertTrue(response.data['image'][k], response.data)

    def test_picture_create_url(self):
        response = self.client.post(_location('picture-list'), {
            'product' : _location('product-detail', pk=1),
            'image': {
                'content': IMAGE_URL,
                'encoding': 'url',
            }
        })
        self.assertEquals(response.status_code, 201, response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('image', response.data, response.data)
        for k in ('thumbnail', 'profile', 'home', 'display'):
            self.assertIn(k, response.data['image'], response.data)
            self.assertTrue(response.data['image'][k], response.data)

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
        self.assertEquals(response.data['product'], None, response.data)
        for k in ('thumbnail', 'profile', 'home', 'display'):
            self.assertIn(k, response.data['image'], response.data)
            self.assertTrue(response.data['image'][k], response.data)
