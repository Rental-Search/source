# -*- coding: utf-8 -*-
from mock import patch
from urllib import urlencode
from urlparse import urlsplit

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from django.utils.translation import ugettext as _

from eloue.products.models import Product
from eloue.wizard import MultiPartFormWizard


class BookingWizardTest(TestCase):
    fixtures = ['patron', 'address', 'price', 'product', 'booking', 'sinister']
    
    def setUp(self):
        self.product = Product.objects.get(pk=1)
    
    def test_zero_step(self):
        response = self.client.get(reverse('booking_create', args=[self.product.slug, self.product.id]))
        self.assertEquals(response.status_code, 200)
    
