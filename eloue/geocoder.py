# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str

from geocoders.google import geocoder


class Geocoder(object):  # TODO : Badly written
    @classmethod
    def geocode(cls, where):
        where = cls.format_place(where)
        coordinates = cache.get('where:%s' % cls.hash_key(where))
        if not coordinates:
            geocode = geocoder(settings.GOOGLE_API_KEY)
            name, coordinates = geocode(where)
            cache.set('where:%s' % cls.hash_key(where), coordinates, 0)
        return coordinates[0], coordinates[1]
    
    @classmethod
    def format_place(cls, where):
        return smart_str(where.strip().lower())
    
    @classmethod
    def hash_key(cls, where):
        return hashlib.md5(where).hexdigest()
