# -*- coding: utf-8 -*-
import os

from django.core.urlresolvers import reverse
from django.test import TestCase

from mock import patch

from eloue.products.models import Picture
from eloue.wizard import MultiPartFormWizard
from eloue.products.models import Product, ProductRelatedMessage, MessageThread
from eloue.accounts.models import Address
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

class ProductWizardTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'picture']
    
    def test_zero_step(self):
        response = self.client.get(reverse('product_create'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_create.html')
    
    def test_first_step_as_anonymous(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        response = self.client.post(reverse('product_create'), {
            '0-category': 484,
            '0-picture': f,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            "0-payment_type":1,
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_register.html')
        self.assertEquals(Picture.objects.count(), 2)
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('product_create'), {
            '0-category': 484,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('product_create'), {
            '0-category': 484,
            '0-picture_id': 1,
            '0-summary': 'Bentley Brooklands',
            '0-day_price': '150',
            '0-deposit_amount': '1500',
            '0-quantity': 1,
            '0-description': 'Voiture de luxe tout confort',
            "0-payment_type":1,
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '11, rue debelleyme',
            '2-addresses__zipcode': '75003',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        l = len(Product.objects.all())
        self.assertRedirects(response, reverse('booking_create', args=['auto-et-moto/voiture/voiture-de-luxe/', 'bentley-brooklands', l]))
        
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_first_step_message_wizard_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('message_create', args=[1, 1]), {
            '0-subject': 'Ask for price, test for wizard',
            '0-body': 'May I have a lower price? never send me a email',
            'wizard_step': 0
        })
        self.assertTemplateUsed(response, 'django_messages/message_register.html')

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_message_wizard_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('message_create', args=[6, 4]), {
            '0-subject': 'Ask for price, test for wizard',
            '0-body': 'May I have a lower price? never send me a email',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 301)
        product = Product.objects.get(pk=6)
        thread = MessageThread.objects.get(pk=1)
        self.assertEqual(thread.subject, 'Ask for price, test for wizard')
        self.assertEqual(product, thread.product)

class AlertWizardTest(TestCase):
    fixtures = ['patron', 'address']
    
    def test_zero_step(self):
        response = self.client.get(reverse('alert_create'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/alert_create.html')
    
    def test_first_step_as_anonymous(self):
        response = self.client.post(reverse('alert_create'), {
            '0-designation': 'Perceuse',
            '0-description': 'J ai besoin d une perceuse pour percer des trou dans le béton'
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/alert_register.html')

    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('alert_create'), {
            '0-designation': 'Perceuse',
            '0-description': 'J ai besoin d une perceuse pour percer des trou dans le béton',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 1
        })
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/alert_missing.html')
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_third_step_as_anonymous(self, mock_method):
        mock_method.return_value = '6941fd7b20d720833717a1f92e8027af'
        response = self.client.post(reverse('alert_create'), {
            '0-designation': 'Perceuse',
            '0-description': 'J ai besoin d une perceuse pour percer des trou dans le béton',
            '1-email': 'alexandre.woog@e-loue.com',
            '1-exists': 1,
            '1-password': 'alexandre',
            '2-phones__phone': '0123456789',
            '2-addresses__address1': '7, rue claude chahu',
            '2-addresses__zipcode': '75016',
            '2-addresses__city': 'Paris',
            '2-addresses__country': 'FR',
            'hash_0': '6941fd7b20d720833717a1f92e8027af',
            'hash_1': '6941fd7b20d720833717a1f92e8027af',
            'wizard_step': 2
        })
        self.assertRedirects(response, reverse('alert_edit'))


