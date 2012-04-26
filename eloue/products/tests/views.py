# -*- coding: utf-8 -*-
import django.forms as forms
from django.core.urlresolvers import reverse
from django.test import TestCase
from eloue.accounts.models import Patron
from eloue.products.models import Product, ProductRelatedMessage, MessageThread
from django_messages import utils
from django_messages.utils import new_message_email
from eloue.signals import message_content_filter, message_site_filter


class ProductViewsTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def setUp(self):
        self.called = False
        def dummy_new_message_email(sender, instance, signal, 
                subject_prefix="",
                template_name="",
                default_protocol=None,
                *args, **kwargs):
            self.called = True
        utils.new_message_email = dummy_new_message_email

    def tearDown(self):
        utils.new_message_email = new_message_email
        
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_product_edit_form(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('owner_product_edit', args=['perceuse-visseuse-philips', 1]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('product' in response.context)
        self.assertTrue(isinstance(response.context['form'], forms.ModelForm))
        self.assertTrue(isinstance(response.context['product'], Product))
        self.assertEqual(response.context['product'].pk, 1)
    
    def test_product_edit(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('owner_product_edit', args=['perceuse-visseuse-philips', 1]), {
            'category': 1,
            'summary': 'Perceuse visseuse Philips',
            'quantity': 1,
            'description': "Engrenage plantaire haute performance 2 vitesses.",
            'deposit_amount': 250
        })
        product = Product.objects.get(pk=1)
        self.assertTrue(response.status_code, 302)
        self.assertEqual(product.description, "Engrenage plantaire haute performance 2 vitesses.")
        self.assertEqual(product.prices.day().count(), 1)
        self.assertEqual(product.prices.day()[0].amount, 24)

    def test_product_price_edit(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('owner_product_price_edit', args=['perceuse-visseuse-philips', 1]), {
            'day_price': 100,
            'deposit_amount': 250,
        })
        product = Product.objects.get(pk=1)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(product.description, u"Engrenage plantaire haute performance 2 vitesses : dur\u00e9e de vie sup\u00e9rieure, transmission optimale, fonctionnement r\u00e9gulier.")
        self.assertEqual(product.prices.day().count(), 1)
        self.assertEqual(product.prices.day()[0].amount, 100)

    def test_product_edit_form_with_nonpositive_price(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('owner_product_price_edit', args=['perceuse-visseuse-philips', 1]), {
            'day_price': 0,
            'deposit_amount': 250,
        })
        product = Product.objects.get(pk=1)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(product.description, u"Engrenage plantaire haute performance 2 vitesses : dur\u00e9e de vie sup\u00e9rieure, transmission optimale, fonctionnement r\u00e9gulier.")
        self.assertEqual(product.prices.day().count(), 1)
        self.assertEqual(product.prices.day()[0].amount, 24)
        
        
    def test_product_edit_when_no_owner(self):
        self.client.login(username='timothee.peignier@e-loue.com', password='timothee')
        response = self.client.get(reverse('owner_product_edit', args=['perceuse-visseuse-philips', 1]))
        self.assertEqual(response.status_code, 403)
    
    def test_product_list(self):
        response = self.client.get('/location/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/location/page/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/location/page/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/nsfw/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-loueur/secret/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-categorie/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/par-condiment/ketchup/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/location/condiment/ketchup/')
        self.assertEqual(response.status_code, 404)
    
    def test_compose_product_related_message(self):
        self.client.login(username='timothee.peignier@e-loue.com', password='timothee')
        sender = Patron.objects.get(email='timothee.peignier@e-loue.com')
        recipient = Patron.objects.get(email='alexandre.woog@e-loue.com')
        recipient.new_messages_alerted = False
        recipient.save()
        response = self.client.post(reverse('message_create', kwargs={'product_id': recipient.products.all()[0].pk, 'recipient_id': recipient.pk}), {
            '0-subject': 'Hi!',
            '0-body': 'How are you?'
        })
        self.assertEqual(len(MessageThread.objects.all()), 1)
        self.assertEqual(len(ProductRelatedMessage.objects.all()), 1)
        thread = MessageThread.objects.all()[0]
        message = ProductRelatedMessage.objects.all()[0]
        self.assertEqual(thread.subject, 'Hi!')
        self.assertEqual(thread.last_message, message)
        self.assertEqual(message.parent_msg, None)
        self.assertEqual(message.thread, thread)
        self.client.logout()

        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        sender, recipient = recipient, sender
        recipient.new_message_alerted = False
        recipient.save()
        response = self.client.post(reverse('thread_details', kwargs={'thread_id': thread.pk}), {'0-body': "I'm fine. And you?"})
        self.assertEqual(len(MessageThread.objects.all()), 1)
        self.assertEqual(len(ProductRelatedMessage.objects.all()), 2)
        thread = MessageThread.objects.all()[0]
        self.assertEqual(thread.last_message.parent_msg.pk, message.pk)
        self.assertEqual(thread.subject, 'Hi!')
        self.assertEqual(thread.last_message.subject, 'Hi!')
        self.assertEqual(thread.last_message.parent_msg.subject, 'Hi!')
        self.client.logout()


    # def test_compose_product_related_message(self):
    #     self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
    #     recipient = Patron.objects.get(email='timothee.peignier@e-loue.com')
    #     recipient.new_messages_alerted = False
    #     recipient.save()
    #     response = self.client.post(reverse('compose_product_related_message'), {
    #         'recipient': 'tim',
    #         'subject': 'Ask for price',
    #         'body': 'May I have a lower price? never send me a email'
    #     })
    #     self.assertTrue(response.status_code, 200)
    #     self.assertEqual(self.called, False)
    
    
    # def test_reply_product_related_message(self):
    #     self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
    #     response = self.client.post(reverse('compose_product_related_message'), {
    #         'recipient': 'lin',
    #         'subject': 'Ask for price',
    #         'body': 'May I have a lower price?, send me email'
    #     })
    #     self.assertEqual(self.called, True)
    #     self.client.logout()
    #     self.client.login(username='lin.liu@e-loue.com', password='lin')
    #     parent_m = ProductRelatedMessage.objects.get(pk=1)
        
    #     response = self.client.post(reverse('reply_product_related_message', args=[parent_m.pk]), {
    #             'subject': 'Reply Ask for price',
    #             'body': 'May I have a lower price? never send me a email'
    #     })
    #     self.assertTrue(response.status_code, 200)
    #     messages = ProductRelatedMessage.objects.all()
    #     self.assertEqual(len(messages), 2)
    #     self.assertEqual(messages[0].product, messages[1].product)

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
    
    def test_alert_list(self):
        response = self.client.get('/location/alertes/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/location/alertes/page/')
        self.assertEqual(response.status_code, 404)
        
    def test_alert_edit(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('alert_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('alert_list' in response.context)
    
    def test_alert_delete(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('alert_delete', args=[1]))
        self.assertTrue(response.status_code, 200)
        

