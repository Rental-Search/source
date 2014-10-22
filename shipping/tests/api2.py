# coding=utf-8
from django.core.urlresolvers import reverse
from django.db.models import get_model
from rest_framework import status
from rest_framework.test import APITestCase


def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)


class ShippingPointTest(APITestCase):

    fixtures = ['patron']

    def setUp(self):
        self.model = get_model('shipping', 'ShippingPoint')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_get_points_by_position(self):
        response = self.client.get(_location('shippingpoint-list'), {
            'lat': 48.856614,
            'lng': 2.3522219000000177,
            'search_type': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, response)
        self.assertGreater(len(response.data), 0, response.data)

    def test_get_points_by_address(self):
        response = self.client.get(_location('shippingpoint-list'), {
            'address': 'Paris',
            'search_type': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, response)
        self.assertGreater(len(response.data), 0, response.data)
