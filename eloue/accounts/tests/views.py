# -*- coding: utf-8 -*-
import urllib

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
    
    def test_create_account_ipn(self):
        data = {
            'first_name': 'Alexandre',
            'account_key': 'AA-4V173529HW897353N',
            'notify_version': 'UNVERSIONED',
            'confirmation_code': '14790711992665769334',
            'charset': 'windows-1252',
            'last_name': 'Woog',
            'verify_sign': 'A5Fxkw0f4nls2IP7F5aSdoTP4lQ6AK8.gKqZPKHFinqPnP6XZB37toxy',
            'test_ipn': '1'
        }
        response = self.client.post(reverse('create_account_ipn'), urllib.urlencode(data), content_type='application/x-www-form-urlencoded; charset=windows-1252;')
        self.failUnlessEqual(response.status_code, 200)
    
