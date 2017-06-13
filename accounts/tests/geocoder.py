# -*- coding: utf-8 -*-
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.test import TestCase
from mock import patch

from eloue.geocoder import Geocoder, GoogleGeocoder

JSON_OUTPUT = StringIO("""{
  "status": "OK",
  "results": [ {
    "types": [ "street_address" ],
    "formatted_address": "11 Rue Debelleyme, 75003 Paris, France",
    "address_components": [ {
      "long_name": "11",
      "short_name": "11",
      "types": [ "street_number" ]
    }, {
      "long_name": "Rue Debelleyme",
      "short_name": "Rue Debelleyme",
      "types": [ "route" ]
    }, {
      "long_name": "3rd arrondissement of Paris",
      "short_name": "3rd arrondissement of Paris",
      "types": [ "sublocality", "political" ]
    }, {
      "long_name": "Paris",
      "short_name": "Paris",
      "types": [ "locality", "political" ]
    }, {
      "long_name": "Paris",
      "short_name": "75",
      "types": [ "administrative_area_level_2", "political" ]
    }, {
      "long_name": "Ile-de-France",
      "short_name": "IDF",
      "types": [ "administrative_area_level_1", "political" ]
    }, {
      "long_name": "France",
      "short_name": "FR",
      "types": [ "country", "political" ]
    }, {
      "long_name": "75003",
      "short_name": "75003",
      "types": [ "postal_code" ]
    } ],
    "geometry": {
      "location": {
        "lat": 48.8613232,
        "lng": 2.3631101
      },
      "location_type": "RANGE_INTERPOLATED",
      "viewport": {
        "southwest": {
          "lat": 48.8581754,
          "lng": 2.3599695
        },
        "northeast": {
          "lat": 48.8644707,
          "lng": 2.3662647
        }
      },
      "bounds": {
        "southwest": {
          "lat": 48.8613229,
          "lng": 2.3631101
        },
        "northeast": {
          "lat": 48.8613232,
          "lng": 2.3631241
        }
      }
    }
  } ]
}""")


class GeocoderTest(TestCase):
    @patch.object(Geocoder, '_geocode')
    def test_geocoder_without_cache(self, mock_method):
        mock_method.return_value = ('11 Rue Debelleyme, 75003 Paris, France', (48.8613232, 2.3631101), 1)
        name, coordinates, radius = Geocoder(use_cache=False).geocode('11 rue debelleyme, 75003 Paris')
        self.assertTrue(mock_method.called)
        self.assertTrue(isinstance(coordinates, tuple))
        self.assertTrue(isinstance(name, basestring))
        self.assertTrue(isinstance(radius, int))
    
    @patch('urllib.urlopen')
    def test_google_geocoder(self, mock_func):
        mock_func.return_value = JSON_OUTPUT
        name, coordinates, radius = GoogleGeocoder(use_cache=False).geocode('11 rue debelleyme, 75003 Paris')
        self.assertTrue(mock_func.called)
        self.assertTrue(isinstance(coordinates, tuple))
        self.assertTrue(isinstance(name, basestring))
        self.assertTrue(isinstance(radius, int))
    
