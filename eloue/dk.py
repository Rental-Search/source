import os

from eloue.settings import *

TIME_ZONE = 'Europe/Copenhagen'

LANGUAGE_CODE = 'da'


DEFAULT_LOCATION = env("DEFAULT_LOCATION", {
    'city': u'Copenhague',
    'coordinates': (55.6760968, 12.5683371),
    'country': u'Danemark',
    'fallback': None,
    'radius': 22,
    'formatted_address': u'Copenhague, Danemark',
    'region': u'Hovedstaden',
    'region_coords': (55.6751812, 12.54932610000003),
    'region_radius': 100,
})
