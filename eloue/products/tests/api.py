# -*- coding: utf-8 -*-
from base64 import encodestring
import oauth2 as oauth
import os
import urlparse

from datetime import datetime, timedelta
from decimal import Decimal as D
from haystack import site
from urllib import urlencode

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import Client, TestCase
from django.utils import simplejson

from eloue.accounts.models import Patron
from eloue.products.models import Product
from eloue.rent.models import Booking


OAUTH_CONSUMER_KEY = '451cffaa88bd49e881068349b093598a'
OAUTH_CONSUMER_SECRET = 'j5rdVtVhKu4VfykM'
OAUTH_TOKEN_KEY = '55e5fc1bd8d2436697a9b3933e475375'
OAUTH_TOKEN_SECRET = '5mhG9J4CE8cM3D37'

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ApiTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'oauth', 'price', 'product']
    
    def setUp(self):
        self.index = site.get_index(Product)
        for product in Product.objects.all():
            self.index.update_object(product)
    
    def _get_request(self, method='GET', parameters=None, use_token=True):
        consumer = oauth.Consumer(OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET)
        print consumer
        if use_token:
            token = oauth.Token(OAUTH_TOKEN_KEY, OAUTH_TOKEN_SECRET)
            print token
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
    
    def test_login_headless(self):
        print "enter test login headless"
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse("auth_login_headless"))
        self.assertTrue(response.status_code, 200)
        csrf_token = response.content
        response = client.post(reverse("auth_login_headless"), {
            "password": 'eloue',
            "email": 'xinlei.chen@e-loue.com',
            "exists": 1,
            "csrfmiddlewaretoken": csrf_token
        })
        self.assertTrue(response.status_code, 200)
    
    def test_request_token(self):
        print "test request token"
        self.client.login(username='benoit.woj@gmail.com', password='ben')
        request = self._get_request(method='GET', use_token=False)
        response = self.client.get(reverse('oauth_request_token'), {'oauth_callback': 'oob'},
            **self._get_headers(request))
        self.assertTrue(response.status_code, 200)
        request_token = dict(urlparse.parse_qsl(response.content))
        self.assertTrue('oauth_token' in request_token)
    
    def test_product_list(self):
        print "product list"
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']),
            {'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Product.objects.count())
    
    def test_product_search(self):
        print "product search"
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {'q': 'perceuse',
            'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], 2)
        
        
    def test_product_search_with_location(self):
        settings.DEBUG = True
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
                Booking.calculate_price(Product.objects.get(pk=product['id']), start_at, end_at)[1])
    
    def test_product_creation(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        post_data = {
            'summary': 'Tondeuse',
            'description': 'Merveilleuse tondeuse',
            'quantity': 1,
            'price': "15.2",
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
        num = Product.objects.count()
        product = Product.objects.get(pk=num)
        self.assertTrue(response["Location"].endswith(product.get_absolute_url()))
        self.assertEquals(product.summary, 'Tondeuse')
        self.assertEquals(product.description, 'Merveilleuse tondeuse')
        self.assertEquals(product.quantity, 1)
        self.assertEquals(product.category.id, 390)
        self.assertEquals(product.address.id, 1)
        self.assertEquals(product.pictures.count(), 1)
    
    def test_account_creation(self):
        post_data = {
            'username': 'chuck',
            'password': 'begood',
            'email': 'chuck.berry@chess-records.com'
        }
        request = self._get_request(method='POST')
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'user']),
            data=simplejson.dumps(post_data),
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
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'user']),
            data=simplejson.dumps(post_data),
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
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'user']),
            data=simplejson.dumps(post_data),
            content_type='application/json',
            **self._get_headers(request))
        self.assertEquals(response.status_code, 400)
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def test_booking_list(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'booking']),
            {'oauth_consumer_key': OAUTH_CONSUMER_KEY})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Booking.objects.count())
                
    def test_booking_calculate_price(self):
        url_dic = {'borrower': '/api/1.0/user/2575/',
                    'ended_at': '2011-01-03 08:00:00',
                    'product': '/api/1.0/product/12199/',
                    'started_at': '2010-12-23 08:00:00'}
        url = urlencode(url_dic)
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'booking'])+"?"+url,
                                    {'oauth_consumer_key':OAUTH_CONSUME_KEY})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['objects'][0]['total_amount'], 275)
                
    def test_booking_creation(self):
        post_data = {
               'started_at': '2010-12-29 08:00:00',
               'ended_at': '2011-01-05 08:00:00',
               'product': '/api/1.0/product/12199/',
                'borrower':'/api/1.0/user/2575/'
                } 
            
        request = self._get_request(method='POST')
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'booking']), 
                                    data=simplejson.dumps(post_data),
                                    content_type='application/json',
                                    **self._get_headers(request))
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        booking = Booking.objects.get(pk=int(response['Location'].split('/')[-2]))
        self.assertEquals(booking.borrower.id, 2575)
        self.assertEquals(booking.product.id, 12199)
        self.assertEquals(booking.started_at, '2010-12-29 08:00:00')
        self.assertEquals(booking.ended_at, '2011-01-05 08:00:00')
        self.assertEquals(booking.total_amount, 175)
        
    def test_booking_auth_to_pending(self):
        post_data = {
               'uuid': 'ae3d2afd-3bb1-4c03-b30f-9ade7de45e91',
               'status': 'pending'
                } 
            
        request = self._get_request(method='POST')
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'booking']), 
                                    data=simplejson.dumps(post_data),
                                    content_type='application/json',
                                    **self._get_headers(request))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('Location' in response)
        booking = Booking.objects.get(pk=post_data['uuid'])
        self.assertEquals(booking.state, "pending")
                   
    def test_booking_auth_to_rejected(self):
        post_data = {
               'uuid': 'ae3d2afd-3bb1-4c03-b30f-9ade7de45e91',
               'status': 'pending'
                } 
            
        request = self._get_request(method='POST')
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'booking']), 
                                    data=simplejson.dumps(post_data),
                                    content_type='application/json',
                                    **self._get_headers(request))
        self.assertEquals(response.status_code, 200)
        #self.assertTrue('Location' in response)
        booking = Booking.objects.get(pk=post_data['uuid'])
        self.assertEquals(booking.state, "rejected")
                   
    def test_booking_closing_to_closed(self):
        post_data = {
               'uuid': 'ae3d2afd-3bb1-4c03-b30f-9ade7de45e91',
               'status': 'pending'
                } 
            
        request = self._get_request(method='POST')
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'booking']), 
                                    data=simplejson.dumps(post_data),
                                    content_type='application/json',
                                    **self._get_headers(request))
        self.assertEquals(response.status_code, 200)
        #self.assertTrue('Location' in response)
        booking = Booking.objects.get(pk=post_data['uuid'])
        self.assertEquals(booking.state, "closed")
        
    def tearDown(self):
        for product in Product.objects.all():
            self.index.remove_object(product)
    
