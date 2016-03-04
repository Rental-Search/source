# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 14
VERTICAL_SITE_NAME = 'autovoisin'

CACHE_MIDDLEWARE_KEY_PREFIX = VERTICAL_SITE_NAME

SECRET_KEY = 'j$(so*u7+=^@64&(skv1qc%avh04lib*)vih_wi7h(bcfx@753'

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace(
            '.css', '_%s.css' % VERTICAL_SITE_NAME)
    PIPELINE_CSS[key]['output_filename'] = output_filename

TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/%s' % VERTICAL_SITE_NAME),
    local_path('templates/'),
))

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [
    2701, 2702, 2703, 2704, 2705, 2706, 2707, 2710,  # first line / nav bar
    2708, 2711, 2712,  # others / dropdown selection  #2709 - minibus
])

FILTER_CATEGORIES = env('FILTER_CATEGORIES', NAVBAR_CATEGORIES)

DASHBOARD_REDIRECT_DOMAIN = env('DASHBOARD_REDIRECT_DOMAIN', 'www.e-loue.com')

ANALYTICS.update({
             'GOOGLE_ID': 'UA-61044932-1',
             'FACEBOOK_ID': '926313257437753',
             'SEGMENT_ID': 'n2kUgtK68yCoincEcsFNO4Xgkaw6PrUi',
             })
