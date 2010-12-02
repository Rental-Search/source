# -*- coding: utf-8 -*-
from base64 import encodestring
import oauth2 as oauth
import os
import time
import urlparse

from urllib import urlencode
from datetime import datetime, timedelta
from decimal import Decimal as D
from haystack import site

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson

from eloue.products.models import Product
from eloue.rent.models import Booking

OAUTH_CONSUMER_KEY = '451cffaa88bd49e881068349b093598a'
OAUTH_CONSUMER_SECRET = 'j5rdVtVhKu4VfykM'
OAUTH_TOKEN_KEY = '87a9386519d24d2a8977388d4fd2e9b5'
OAUTH_TOKEN_SECRET = 'jSdFZCdLgzTCRxcG'

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ApiProductResourceTest(TestCase):
    fixtures = ['patron', 'address', 'oauth', 'price', 'product']
    
    def setUp(self):
        self.index = site.get_index(Product)
        for product in Product.objects.all():
            self.index.update_object(product)
    
    def _get_request(self, method='GET', parameters=None):
        consumer = oauth.Consumer(OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET)
        token = oauth.Token(OAUTH_TOKEN_KEY, OAUTH_TOKEN_SECRET)
        request = oauth.Request.from_consumer_and_token(consumer, token, http_method=method, parameters=parameters)
        request.sign_request(oauth.SignatureMethod_PLAINTEXT(), consumer, token)
        return request
    
    def _get_headers(self, request):
        headers = request.to_header()
        headers['HTTP_AUTHORIZATION'] = headers['Authorization']
        del headers['Authorization']
        return headers
    
    def test_product_list(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']),
            {'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Product.objects.count())
    
    def test_product_search(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {'q': 'perceuse',
            'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], 2)
    
    def test_product_search_with_location(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {
            'q': 'perceuse', 'l': '48.8613232, 2.3631101', 'r': 1,
            'oauth_consumer_key': OAUTH_CONSUMER_KEY
        })
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], 2)
    
    def test_product_with_dates(self):
        start_at = datetime.now() + timedelta(days=1)
        end_at = start_at + timedelta(days=1)
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {
            'date_start': start_at.isoformat(),
            'date_end': end_at.isoformat(),
            'oauth_consumer_key': OAUTH_CONSUMER_KEY
        })
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Product.objects.count())
        for product in json['objects']:
            self.assertEquals(D(product['price']),
                Booking.calculate_price(Product.objects.get(pk=product['id']), start_at, end_at))
    
    def test_product_creation(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        post_data = {
            'summary':'Tondeuse',
            'description': 'Merveilleuse tondeuse',
            'quantity': 1,
            'deposit_amount': 150,
            'picture': encodestring(f.read()),
            'category': '/api/1.0/category/390/',
            'address': '/api/1.0/address/1/'
        }
        request = self._get_request(method='POST')
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'product']),
            data=simplejson.dumps(post_data),
            content_type='application/json',
            **self._get_headers(request))
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        product = Product.objects.get(pk=int(response['Location'].split('/')[-2]))
        self.assertEquals(product.summary, 'Tondeuse')
        self.assertEquals(product.description, 'Merveilleuse tondeuse')
        self.assertEquals(product.quantity, 1)
        self.assertEquals(product.category.id, 390)
        self.assertEquals(product.address.id, 1)
        self.assertEquals(product.pictures.count(), 1)
    
    def tearDown(self):
        for product in Product.objects.all():
            self.index.remove_object(product)
    
