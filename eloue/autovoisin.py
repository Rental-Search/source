# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 14
VERTICAL_SITE_NAME = 'autovoisin'

CACHE_MIDDLEWARE_KEY_PREFIX = VERTICAL_SITE_NAME

SECRET_KEY = 'j$(so*u7+=^@64&(skv1qc%avh04lib*)vih_wi7h(bcfx@753'

SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', VERTICAL_SITE_NAME)

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace(
            '.css', '_%s.css' % VERTICAL_SITE_NAME)
    PIPELINE_CSS[key]['output_filename'] = output_filename

TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/%s' % VERTICAL_SITE_NAME),
    local_path('templates/'),
))

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [
    2701, 2702, 2703, 2704, 2705, 2706, 2707, 2708,  # first line / nav bar
    2709, 2710, 2711, 2712,  # others / dropdown selection
])

FILTER_CATEGORIES = env('FILTER_CATEGORIES', NAVBAR_CATEGORIES)

DASHBOARD_REDIRECT_DOMAIN = env('DASHBOARD_REDIRECT_DOMAIN', 'www.e-loue.com')
