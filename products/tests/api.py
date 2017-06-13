# -*- coding: utf-8 -*-
from base64 import encodestring
import oauth2 as oauth
import os
import urlparse

from datetime import datetime, timedelta
from decimal import Decimal as D

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import Client, TransactionTestCase

import haystack

from accounts.models import Patron
from products.models import Product,ProductRelatedMessage
from rent.models import Booking

from eloue.utils import json


OAUTH_CONSUMER_KEY = '451cffaa88bd49e881068349b093598a'
OAUTH_CONSUMER_SECRET = 'j5rdVtVhKu4VfykM'
OAUTH_TOKEN_KEY = '87a9386519d24d2a8977388d4fd2e9b5'
OAUTH_TOKEN_SECRET = 'jSdFZCdLgzTCRxcG'

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ApiTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'oauth', 'price', 'product', 'booking_api', 'phones', 'messagethread', 'message']

    def setUp(self):
        conn = haystack.connections[haystack.constants.DEFAULT_ALIAS]
        backend = conn.get_backend()
        index = conn.get_unified_index().get_index(Product)
        backend.update(index, index.build_queryset())

    def tearDown(self):
        conn = haystack.connections[haystack.constants.DEFAULT_ALIAS]
        backend = conn.get_backend()
        for obj in Product.objects.all():
            backend.remove(obj)

    def _get_request(self, method='GET', parameters=None, use_token=True):
        consumer = oauth.Consumer(OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET)
        if use_token:
            token = oauth.Token(OAUTH_TOKEN_KEY, OAUTH_TOKEN_SECRET)
        else:
            token = None
        request = oauth.Request.from_consumer_and_token(consumer, token, http_method=method, parameters=parameters)
        request.sign_request(oauth.SignatureMethod_PLAINTEXT(), consumer, token)
        return request

    def _get_headers(self, request):
        headers = request.to_header()
        headers['HTTP_AUTHORIZATION'] = headers['Authorization']
        del headers['Authorization']
        return headers

    def _resource_url(self, resource_name, resource_id=None):
        url = reverse("api_dispatch_list", args=['1.0', resource_name])
        if resource_id:
            return "%s%s/" % (url, resource_id)
        return url


    def test_login_headless(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse("auth_login_headless"))
        self.assertTrue(response.status_code, 200)
        csrf_token = response.content
        response = client.post(reverse("auth_login_headless"), {
            "password": 'alexandre',
            "email": 'alexandre.woog@e-loue.com',
            "exists": 1,
            "csrfmiddlewaretoken": csrf_token
        })
        self.assertTrue(response.status_code, 200)
    
    def test_request_token(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        request = self._get_request(method='GET', use_token=False)
        response = self.client.get(reverse('oauth_request_token'), {'oauth_callback': 'oob'},
            **self._get_headers(request))
        self.assertTrue(response.status_code, 200)
        request_token = dict(urlparse.parse_qsl(response.content))
        self.assertTrue('oauth_token' in request_token)
    
    def test_product_list(self):
        response = self.client.get(self._resource_url('product'),
            {'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertEquals(json_res['meta']['total_count'], Product.objects.count())
    
    def test_product_search(self):
        response = self.client.get(self._resource_url('product'), {'q': 'perceuse',
            'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertEquals(json_res['meta']['total_count'], 3)
        
        
    def test_product_search_with_location(self):
        settings.DEBUG = True
        response = self.client.get(self._resource_url('product'), {
            'q': 'perceuse', 'l': '48.8613232, 2.3631101', 'r': 1,
            'oauth_consumer_key': OAUTH_CONSUMER_KEY
        })
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertEquals(json_res['meta']['total_count'], 3)
    
    def test_product_with_dates(self):
        start_at = datetime.now() + timedelta(days=1)
        end_at = start_at + timedelta(days=1)
        response = self.client.get(self._resource_url('product'), {
            'date_start': start_at.isoformat(),
            'date_end': end_at.isoformat(),
            'oauth_consumer_key': OAUTH_CONSUMER_KEY
        })
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertEquals(json_res['meta']['total_count'], Product.objects.count())
        for product in json_res['objects']:
            self.assertEquals(D(product['price']),
                Product.objects.get(pk=product['id']).calculate_price(start_at, end_at)[1])
    
    def test_product_creation(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        post_data = {
            'summary': 'Tondeuse',
            'description': 'Merveilleuse tondeuse',
            'quantity': 1,
            'price': "15.2",
            'deposit_amount': 150,
            'picture': encodestring(f.read()),
            'category': '/api/1.0/category/1/',
            'address': '/api/1.0/address/1/'
        }
        request = self._get_request(method='POST')
        response = self.client.post(self._resource_url('product'),
            data=json.dumps(post_data),
            content_type='application/json',
            **self._get_headers(request))
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        num = Product.objects.count()
        product = Product.objects.get(pk=num)
        self.assertTrue(response["Location"].endswith(product.get_absolute_url()))
        self.assertEquals(product.summary, 'Tondeuse')
        self.assertEquals(product.description, 'Merveilleuse tondeuse')
        self.assertEquals(product.quantity, 1)
        self.assertEquals(product.category.id, 1)
        self.assertEquals(product.address.id, 1)
        self.assertEquals(product.pictures.count(), 1)
    
    def test_account_creation(self):
        post_data = {
            'username': 'chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com'
        }
        request = self._get_request(method='POST')
        response = self.client.post(self._resource_url('user'),
            data=json.dumps(post_data),
            content_type='application/json',
            **self._get_headers(request))
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        patron = Patron.objects.get(pk=int(response['Location'].split('/')[-2]))
        self.assertEquals(patron.username, 'chuck')
        self.assertEquals(patron.email, 'chuck.berry@chess-records.com')
        self.assertEquals(patron.is_active, True)
    
    @transaction.commit_on_success
    def test_account_creation_with_duplicate_email(self):
        post_data = {
            'username': 'chuck.berry',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com'
        }
        request = self._get_request(method='POST')
        response = self.client.post(self._resource_url('user'),
            data=json.dumps(post_data),
            content_type='application/json',
            **self._get_headers(request))
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        post_data = {
            'username': 'berry.chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com'
        }
        request = self._get_request(method='POST')
        response = self.client.post(self._resource_url('user'),
            data=json.dumps(post_data),
            content_type='application/json',
            **self._get_headers(request))
        self.assertEquals(response.status_code, 400)

    def test_customer_creation(self):
        login_success = self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        self.assertTrue(login_success)
        post_data = {
            'username': 'customer1',
            'password': 'iwantyourcar',
            'email': 'customer1@customerfarm.com'
        }
        headers = self._get_headers(self._get_request(method='POST'))
        response = self.client.post(
            self._resource_url('customer'),
            data=json.dumps(post_data),
            content_type='application/json',
            **headers
        )
        customer = Patron.objects.get(username='customer1')
        renter = Patron.objects.get(email='alexandre.woog@e-loue.com')
        rcust = renter.customers.get(username='customer1')
        self.assertEquals(customer, rcust)

    def test_customer_list(self):
        login_success = self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        self.assertTrue(login_success)
        users_data = [
            {
                'username': 'customer1',
                'password': 'iwantyourcar',
                'email': 'customer1@customerfarm.com'
            },
            {
                'username': 'customer2',
                'password': 'iwantyourcartoo',
                'email': 'customer2@customerfarm.com'
            }
        ]

        
        for data in users_data:
            headers = self._get_headers(self._get_request(method='POST'))
            response_post = self.client.post(
                self._resource_url('customer'),
                data=json.dumps(data),
                content_type='application/json',
                **headers
            )

        headers = self._get_headers(self._get_request(method='GET'))
        response = self.client.get(
            self._resource_url('customer'),
            **headers
        )
        content = json.loads(response.content)
        self.assertEquals(content["meta"]["total_count"], 2)

    def test_user_modification(self):
        login_success = self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        self.assertTrue(login_success)
        headers = self._get_headers(self._get_request(method='PUT'))
        myid = Patron.objects.get(email='alexandre.woog@e-loue.com').id
        response = self.client.put(
            self._resource_url('user', myid),
            data=json.dumps({'username':'trololol'}),
            content_type='application/json',
            **headers
        )
        self.assertEquals(response.status_code, 204)
        patron = Patron.objects.get(email='alexandre.woog@e-loue.com')
        self.assertEquals(patron.username, 'trololol')
        
    def test_message_list(self):
        request = self._get_request(method='GET', use_token=True)
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'message']), 
                                            **self._get_headers(request))
        self.assertEquals(response.status_code, 200)
        json_res = json.loads(response.content)
        self.assertEquals(json_res['meta']['total_count'],2)
        
    def test_message_creation(self):
        post_data = {"body": "test body", 
                     "product": "/api/1.0/product/6/", 
                     "subject": "test subject",
                     "parent_msg": "/api/1.0/message/2/",
                     "thread": 1,
                     "recipient": "/api/1.0/user/4/"}
        request = self._get_request(method='POST', use_token=True)
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'message']), 
                                    data=json.dumps(post_data),
                                    content_type='application/json',
                                    **self._get_headers(request))
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        message = ProductRelatedMessage.objects.get(pk=int(response['Location'].split('/')[-2]))
        self.assertEquals(message.sender.id, 1)
        self.assertEquals(message.thread.id, 1)
        self.assertEquals(message.body, 'test body')
        self.assertEquals(message.subject, 'test subject')
