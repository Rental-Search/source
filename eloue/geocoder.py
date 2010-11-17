# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str

from geocoders.google import geocoder


class Geocoder(object):  # TODO : Badly written
    @classmethod
    def geocode(cls, location):
        location = cls.format_place(location)
        coordinates = cache.get('location:%s' % cls.hash_key(location))
        if not coordinates:
            geocode = geocoder(settings.GOOGLE_API_KEY)
            name, coordinates = geocode(location)
            cache.set('location:%s' % cls.hash_key(location), coordinates, 0)
        return coordinates[0], coordinates[1]
    
    @classmethod
    def format_place(cls, location):
        return smart_str(location.strip().lower())
    
    @classmethod
    def hash_key(cls, location):
        return hashlib.md5(location).hexdigest()
