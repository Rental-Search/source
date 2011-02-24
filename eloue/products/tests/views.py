# -*- coding: utf-8 -*-
import django.forms as forms
from django.core.urlresolvers import reverse
from django.test import TestCase

from eloue.products.models import Product


class ProductViewsTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_product_edit_form(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('product_edit', args=['perceuse-visseuse-philips', 1]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('product' in response.context)
        self.assertTrue(isinstance(response.context['form'], forms.ModelForm))
        self.assertTrue(isinstance(response.context['product'], Product))
        self.assertEqual(response.context['product'].pk, 1)
    
    def test_product_edit(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('product_edit', args=['perceuse-visseuse-philips', 1]), {
            'category': 1,
            'summary': 'Perceuse visseuse Philips',
            'day_price': 100,
            'deposit_amount': 250,
            'quantity': 1,
            'description': "Engrenage plantaire haute performance 2 vitesses."
        })
        product = Product.objects.get(pk=1)
        self.assertRedirects(response, product.get_absolute_url(), status_code=301)
        self.assertEqual(product.description, "Engrenage plantaire haute performance 2 vitesses.")
        self.assertEqual(product.prices.day().count(), 1)
        self.assertEqual(product.prices.day()[0].amount, 100)
    
    def test_product_edit_when_no_owner(self):
        self.client.login(username='timothee.peignier@e-loue.com', password='timothee')
        response = self.client.get(reverse('product_edit', args=['perceuse-visseuse-philips', 1]))
        self.assertEqual(response.status_code, 403)
    
    def test_product_list(self):
        response = self.client.get('/location/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/location/page/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/location/page/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-categorie/nsfw/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-loueur/secret/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-categorie/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-condiment/ketchup/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/condiment/ketchup/')
        self.assertEqual(response.status_code, 404)
    
    def test_product_delete(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('product_delete', args=['perceuse-visseuse-philips', 1]))
        self.assertRedirects(response, reverse('owner_product'), status_code=301)
        try:
            Product.objects.get(pk=1)
            self.fail()
        except Product.DoesNotExist:
            pass
    
    def test_product_delete_confirmation(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('product_delete', args=['perceuse-visseuse-philips', 1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_delete.html')
    
