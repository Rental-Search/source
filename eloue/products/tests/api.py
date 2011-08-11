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
from django.db.models import Q
from django.test import Client, TestCase
from django.utils import simplejson

from eloue.accounts.models import Patron
from eloue.products.models import Product
from eloue.rent.models import Booking


OAUTH_CONSUMER_KEY = '451cffaa88bd49e881068349b093598a'
OAUTH_CONSUMER_SECRET = 'j5rdVtVhKu4VfykM'
OAUTH_TOKEN_KEY = '87a9386519d24d2a8977388d4fd2e9b5'
OAUTH_TOKEN_SECRET = 'jSdFZCdLgzTCRxcG'

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ApiTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'oauth', 'price', 'product', 'booking']
    
    def setUp(self):
        self.index = site.get_index(Product)
        for product in Product.objects.all():
            self.index.update_object(product)
    
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
        print simplejson.dumps(post_data)
        print self._get_headers(request)
        print ">>>>>>>>>>>>>>>>>>>>>>>>"
        print "request %s" % response.request
        print "context %s" % response.context 
        print "content %s" % response.content
        
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        patron = Patron.objects.get(pk=int(response['Location'].split('/')[-2]))
        self.assertEquals(patron.username, 'chuck')
        #self.assertEquals(patron.email, 'chuck.berry@chess-records.com')
        self.assertEquals(patron.email, 'chuck.berry@chesdfqsdfsdfqsdfs-records.com')
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
        
    def test_booking_list(self):
        request = self._get_request(method='GET', use_token=True)
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'booking']), HTTP_AUTHORIZATION=request.to_header()['Authorization'])
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Booking.objects.filter( Q(borrower=Patron.objects.get(pk=1)) | Q(owner=Patron.objects.get(pk=1)) ).count())

    def test_booking_calculate_price(self):
        booking_to_cal = {'borrower': '/api/1.0/user/1/',
                          'ended_at': '2011-01-03 08:00:00',
                          'product': '/api/1.0/product/6/',
                          'started_at': '2010-12-23 08:00:00'}
        request = self._get_request(method='GET', use_token=True)
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'booking']), booking_to_cal, HTTP_AUTHORIZATION=request.to_header()['Authorization'])
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['objects'][0]['product'], "/api/1.0/product/6/")
        self.assertEquals(json['objects'][0]['borrower'], "/api/1.0/user/1/")
        self.assertEquals(json['objects'][0]['owner'], "/api/1.0/user/4/")
        self.assertEquals(json['objects'][0]['started_at'], "2010-12-23T08:00:00")
        self.assertEquals(json['objects'][0]['ended_at'], "2011-01-03T08:00:00")
        self.assertEquals(json['objects'][0]['total_amount'], "1980.00")
                
    def test_booking_creation(self):
        post_data = {'started_at': '2010-12-29 08:00:00',
                     'ended_at': '2011-01-05 08:00:00',
                     'product': '/api/1.0/product/6/',
                     'borrower':'/api/1.0/user/1/',
                     'status': 'authorizing'
                    } 
        request = self._get_request(method='POST', use_token=True)
        #print request.to_header()['Authorization']
        #print self._get_headers(request)
        print simplejson.dumps(post_data)
        response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'booking']), 
                                    data=simplejson.dumps(post_data),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=request.to_header()['Authorization'])
                                    #**self._get_headers(request))
        #print "request %s" % response.request
        #print "context %s" % response.context
        #print "body %s" % response.content 
        
        self.assertEquals(response.status_code, 201)
        self.assertTrue('Location' in response)
        booking = Booking.objects.get(pk=int(response['Location'].split('/')[-2]))
        self.assertEquals(booking.borrower.id, 1)
        self.assertEquals(booking.product.id, 6)
        self.assertEquals(booking.started_at, '2010-12-29 08:00:00')
        self.assertEquals(booking.ended_at, '2011-01-05 08:00:00')
        self.assertEquals(booking.total_amount, 1980)
                # 
                # post_data = {
                #     'username': 'chuck',
                #     'password': 'begood',
                #     'email': 'chuck.berry@chess-records.com'
                # }
                # request = self._get_request(method='POST')
                # response = self.client.post(reverse("api_dispatch_list", args=['1.0', 'user']),
                #     data=simplejson.dumps(post_data),
                #     content_type='application/json',
                #     **self._get_headers(request))
                # self.assertEquals(response.status_code, 201)
                # self.assertTrue('Location' in response)
                # patron = Patron.objects.get(pk=int(response['Location'].split('/')[-2]))
                # self.assertEquals(patron.username, 'chuck')
                # self.assertEquals(patron.email, 'chuck.berry@chess-records.com')
                # self.assertEquals(patron.is_active, True)
    def test_booking_auth_to_pending(self):
        post_data = {
               'uuid': 'a72608d9-a7e3-49ce-9ba6-28abfdfc9cb3',
               'status': 'pending'
                } 
            
        request = self._get_request(method='POST')
        client = Client()
        client.login(email="alexandre.woog@e-loue.com", password="alexandre")
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
               'uuid': 'a72608d9a7e349ce9ba628abfdfc9cb3',
               'status': 'rejected'
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
               'uuid': 'a72608d9a7e349ce9ba628abfdfc9cb3',
               'status': 'closed'
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
    
