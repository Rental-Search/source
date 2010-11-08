# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from eloue.products.models import Picture

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ProductWizardTest(TestCase):
    fixtures = ['patron', 'address', 'price', 'product', 'picture']
    
    def setUp(self):
        self.old_secret_key = settings.SECRET_KEY
        settings.SECRET_KEY = "123"
    
    def test_zero_step(self):
        response = self.client.get(reverse('product_create'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_create.html')
    
    def test_first_step_as_anonymous(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        response = self.client.post(reverse('product_create'), {
            '0-category':484,
            '0-picture':f,
            '0-summary':'Bentley Brooklands',
            '0-price':'150',
            '0-deposit_amount':'1500',
            '0-quantity':1,
            '0-description':'Voiture de luxe tout confort',            
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_register.html')
        self.assertEquals(Picture.objects.count(), 2)
    
    def test_second_step_as_anonymous(self):
        response = self.client.post(reverse('product_create'), {
            '0-category':484,
            '0-picture_id':1,
            '0-summary':'Bentley Brooklands',
            '0-price':'150',
            '0-deposit_amount':'1500',
            '0-quantity':1,
            '0-description':'Voiture de luxe tout confort',
            '1-email':'alexandre.woog@e-loue.com',
            '1-exists':1,
            '1-password':'alexandre',
            'hash_0':'6941fd7b20d720833717a1f92e8027af',
            'wizard_step':1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_missing.html')
    
    def test_third_step_as_anonymous(self):
        response = self.client.post(reverse('product_create'), {
            '0-category':484,
            '0-picture_id':1,
            '0-summary':'Bentley Brooklands',
            '0-price':'150',
            '0-deposit_amount':'1500',
            '0-quantity':1,
            '0-description':'Voiture de luxe tout confort',
            '1-email':'alexandre.woog@e-loue.com',
            '1-exists':1,
            '1-password':'alexandre',
            '2-phones__phone':'0123456789',
            '2-addresses__address1':'11, rue debelleyme',
            '2-addresses__zipcode':'75003',
            '2-addresses__city':'Paris',
            '2-addresses__country':'FR',
            'hash_0':'6941fd7b20d720833717a1f92e8027af',
            'hash_1':'f4d8f4af9bcbe43812214e7f85b51d41',
            'wizard_step':2
        })
        self.assertRedirects(response, reverse('product_detail', args=['bentley-brooklands', 5]))
    
    def tearDown(self):
        settings.SECRET_KEY = self.old_secret_key
    
