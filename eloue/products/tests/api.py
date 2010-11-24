# -*- coding: utf-8 -*-
import unittest

from datetime import datetime, timedelta
from decimal import Decimal as D
from haystack import site

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson

from eloue.products.models import Product
from eloue.rent.models import Booking


class ApiProductResourceTest(TestCase):
    fixtures = ['patron', 'address', 'price', 'product']
    
    def setUp(self):
        self.index = site.get_index(Product)
        for product in Product.objects.all():
            self.index.update_object(product)
    
    @unittest.skip
    def test_product_list(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']))
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Product.objects.count())
    
    @unittest.skip
    def test_product_search(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {'q': 'perceuse'})
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], 2)
    
    @unittest.skip
    def test_product_search_with_location(self):
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {
            'q': 'perceuse', 'l': '48.8613232, 2.3631101', 'r': 1
        })
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], 2)
    
    @unittest.skip
    def test_product_with_dates(self):
        start_at = datetime.now() + timedelta(days=1)
        end_at = start_at + timedelta(days=1)
        response = self.client.get(reverse("api_dispatch_list", args=['1.0', 'product']), {
            'date_start': start_at.isoformat(),
            'date_end': end_at.isoformat()
        })
        self.assertEquals(response.status_code, 200)
        json = simplejson.loads(response.content)
        self.assertEquals(json['meta']['total_count'], Product.objects.count())
        for product in json['objects']:
            self.assertEquals(D(product['price']),
                Booking.calculate_price(Product.objects.get(pk=product['id']), start_at, end_at))
    
    def tearDown(self):
        for product in Product.objects.all():
            self.index.remove_object(product)
    
