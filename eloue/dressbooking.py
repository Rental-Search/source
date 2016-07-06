# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 15

CACHE_MIDDLEWARE_KEY_PREFIX = 'dressbooking'


SERVER_EMAIL = 'contact@dressbooking.com'
DEFAULT_FROM_EMAIL = 'contact@dressbooking.com'

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace('.css', '_dressbooking.css')
    PIPELINE_CSS[key]['output_filename'] = output_filename


TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/dressbooking'),
    local_path('templates/'),
))

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [2856, 2879, 2896])

#FILTER_CATEGORIES = env('FILTER_CATEGORIES', NAVBAR_CATEGORIES)

PUBLISH_CATEGORIES = env('PUBLISH_CATEGORIES', (
	(("Femmme", NAVBAR_CATEGORIES[0], "dress"),
    ("Homme", NAVBAR_CATEGORIES[1], "group"),
    ("Enfant", NAVBAR_CATEGORIES[2], "basket")),
))

ALGOLIA_CREDENTIALS['PREFIX'] = 'dressbooking_'

DEFAULT_RADIUS = 600


#DASHBOARD_REDIRECT_DOMAIN = env('DASHBOARD_REDIRECT_DOMAIN', 'www.e-loue.com')

ANALYTICS.update({
                  'GOOGLE_ID': 'UA-77168089-1'
                  })