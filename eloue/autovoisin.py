# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 14

CACHE_MIDDLEWARE_KEY_PREFIX = 'autovoisin'

SECRET_KEY = 'j$(so*u7+=^@64&(skv1qc%avh04lib*)vih_wi7h(bcfx@753'

SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', 'autovoisin')

#for key in PIPELINE_CSS:
#    output_filename = PIPELINE_CSS[key]['output_filename'].replace('.css', '_gosport.css')
#    PIPELINE_CSS[key]['output_filename'] = output_filename
#
#TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
#    local_path('templates/gosport'),
#    local_path('templates/'),
#))

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [
    2701, 2702, 2703, 2704, 2705, 2706, 2707, 2708,  # first line / nav bar
    2709, 2710, 2711, 2712,  # others / dropdown selection
])

FILTER_CATEGORIES = env('FILTER_CATEGORIES', NAVBAR_CATEGORIES)

DASHBOARD_REDIRECT_DOMAIN = env('DASHBOARD_REDIRECT_DOMAIN', 'www.e-loue.com')
