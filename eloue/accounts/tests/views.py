# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase


class PatronTest(TestCase):
    fixtures = ['patron']
    
    def test_patron_detail_view(self):
        response = self.client.get(reverse('patron_detail', args=['alexandre']))
        self.assertEqual(response.status_code, 200)
    
    def test_patron_detail_compat(self):
        response = self.client.get(reverse('patron_detail_compat', args=['alexandre', 1]))
        self.assertRedirects(response, reverse('patron_detail', args=['alexandre']), status_code=301)
    
    def test_patron_login(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)
    
