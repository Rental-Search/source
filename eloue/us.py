import os

from eloue.settings import *

TIME_ZONE = 'America/Los_Angeles'

LANGUAGE_CODE = 'en-US'

VERTICAL_SITE_NAME = 'us'

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace(
            '.css', '_%s.css' % VERTICAL_SITE_NAME)
    PIPELINE_CSS[key]['output_filename'] = output_filename

TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/%s' % VERTICAL_SITE_NAME),
    local_path('templates/'),
))

DEFAULT_LOCATION = env("DEFAULT_LOCATION", {
    'city': u'Los Angeles, California',
    'country_coordinates': (34.0522342, -118.2436849),
    'country': u'United States of America',
    'fallback': None,
    'country_radius': 22,
    'formatted_address': u'Los Angeles, California',
    'region': u'California',
    'region_coords': (34.0522342, -118.2436849),
    'region_radius': 100,
})

#DEFAULT_LOCATION_CITY = env("DEFAULT_LOCATION_CITY", {'city': u"Copenhague, Danemark", 'radius': 200})
