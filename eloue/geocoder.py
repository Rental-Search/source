# -*- coding: utf-8 -*-
import hashlib
import urllib

from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str
from django.utils import simplejson

from geopy import Point, distance

GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', 'ABQIAAAA7bPNcG5t1-bTyW9iNmI-jRRqVDjnV4vohYMgEqqi0RF2UFYT-xSSwfcv2yfC-sACkmL4FuG-A_bScQ')
GOOGLE_REGION_CODE = getattr(settings, 'GOOGLE_REGION_CODE', 'fr')


class Geocoder(object):
    def __init__(self, use_cache=True):
        self.use_cache = use_cache
    
    def geocode(self, location):
        location = self.format_place(location)
        name, lat, lon, radius, cache_hit = None, None, None, None, False
        if self.use_cache:
            cache_value = cache.get('location:%s' % self.hash_key(location))
            if cache_value != None:
                name, (lat, lon), radius = cache_value
                cache_hit = True
        
        if not cache_hit and (lat == None or lon == None):
            name, (lat, lon), radius = self._geocode(location)
        
        if not cache_hit and self.use_cache and not ((lat is None) or (lon is None)):
            cache.set('location:%s' % self.hash_key(location), (name, (lat, lon), radius), 0)
        return name, (lat, lon), radius
    
    def _geocode(self, location):
        raise NotImplementedError
    
    def format_place(self, location):
        """
        >>> geocoder = Geocoder()
        >>> geocoder.format_place(" paris, FRANCE ")
        'paris, france'
        """
        return smart_str(location.strip().lower())
    
    def hash_key(self, location):
        """
        >>> geocoder = Geocoder()
        >>> geocoder.hash_key("paris")
        'ccbee73cd81c7f42405e1920409247ec'
        """
        return hashlib.md5(location).hexdigest()
    

class GoogleGeocoder(Geocoder):
    # http://code.google.com/apis/maps/documentation/geocoding/index.html
    def get_json(self, location):
        return simplejson.load(urllib.urlopen(
            'http://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
                'address': smart_str(location),
                'oe': 'utf8',
                'sensor': 'false',
                'region': GOOGLE_REGION_CODE
            })
        ))

    def _get_radius(self, json):
        try:
            sw = Point(json['results'][0]['geometry']['viewport']['southwest']['lat'],
                json['results'][0]['geometry']['viewport']['southwest']['lng'])
            ne = Point(json['results'][0]['geometry']['viewport']['northeast']['lat'],
                json['results'][0]['geometry']['viewport']['northeast']['lng'])
            radius = (distance.distance(sw, ne).km // 2) + 1
        except (KeyError, IndexError):
            return None
        return radius

    def _geocode(self, location):
        try:
            json = self.get_json(location)
            lon = json['results'][0]['geometry']['location']['lng']
            lat = json['results'][0]['geometry']['location']['lat']
        except (KeyError, IndexError, IOError):
            return None, (None, None), None
        radius = self._get_radius(json)
        if radius is None:
            return None, (lat, lon), None
        name = json['results'][0]['formatted_address']
        return name, (lat, lon), int(radius)
    
    def getCityCountry(self, locationName):
        # returns city and country
        json = self.get_json(locationName)
        return json['results'][0]['address_components'][0]['long_name'], json['results'][0]['address_components'][-1]['short_name']

    def get_departement(self, location):
        json = self.get_json(location)
        try:
            return filter(
                lambda component: 'administrative_area_level_2' in component['types'], 
                json['results'][0]['address_components']
            )[0]
        except (KeyError, IndexError) as e:
            return None

