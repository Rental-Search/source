# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 15

CACHE_MIDDLEWARE_KEY_PREFIX = 'dressbooking'

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace('.css', '_dressbooking.css')
    PIPELINE_CSS[key]['output_filename'] = output_filename


TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/dressbooking'),
    local_path('templates/'),
))

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [2856, 2877, 2894])

#FILTER_CATEGORIES = env('FILTER_CATEGORIES', NAVBAR_CATEGORIES)

PUBLISH_CATEGORIES = env('PUBLISH_CATEGORIES', (
	(("Femmme", NAVBAR_CATEGORIES[0], "robe"),
    ("Homme", NAVBAR_CATEGORIES[1], "Vestes classiques"),
    ("Enfant", NAVBAR_CATEGORIES[2], "Robe et cotèges")),
))

DASHBOARD_REDIRECT_DOMAIN = env('DASHBOARD_REDIRECT_DOMAIN', 'www.e-loue.com')