import os

from eloue.settings import *

TIME_ZONE = 'Europe/Copenhagen'

LANGUAGE_CODE = 'da'

VERTICAL_SITE_NAME = 'dk'

for key in PIPELINE_JS:
    output_filename = PIPELINE_JS[key]['output_filename'].replace(
            '.js', '_%s.js' % VERTICAL_SITE_NAME)
    PIPELINE_JS[key]['output_filename'] = output_filename

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace(
            '.css', '_%s.css' % VERTICAL_SITE_NAME)
    PIPELINE_CSS[key]['output_filename'] = output_filename

TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/%s' % VERTICAL_SITE_NAME),
    local_path('templates/'),
))


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

DEFAULT_LOCATION_CITY = env("DEFAULT_LOCATION_CITY", {'city': u"Copenhague, Danemark", 'radius': 200})

ANALYTICS.update({
                  'GOOGLE_ID': 'UA-8258979-1'
                  })