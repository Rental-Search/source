# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 13

SESSION_COOKIE_DOMAIN = 'go-sport.fr' # FIXME!

CACHE_MIDDLEWARE_KEY_PREFIX = 'gosport'

for key in PIPELINE_CSS:
    output_filename = PIPELINE_CSS[key]['output_filename'].replace('.css', '_gosport.css')
    PIPELINE_CSS[key]['output_filename'] = output_filename

TEMPLATE_DIRS = env('TEMPLATE_DIRS', (
    local_path('templates/gosport'),
    local_path('templates/'),
))

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [
    2846, 2769, 2774, 2762, 2848, 2823, 2808,  # first line / nav bar
    2783, 2840, 2857, 2835,  # others / dropdown selection
])

FILTER_CATEGORIES = env('FILTER_CATEGORIES', NAVBAR_CATEGORIES)

PUBLISH_CATEGORIES = env('PUBLISH_CATEGORIES', (
    ("Sports d'hiver", NAVBAR_CATEGORIES[0], "ski"),
    ("Sports de raquette", NAVBAR_CATEGORIES[1], "tennis"),
    ("Cycles", NAVBAR_CATEGORIES[2], "bike"),
    ("Sports d'extérieur", NAVBAR_CATEGORIES[3], "golf"),
    ("Sports d'équipe", NAVBAR_CATEGORIES[4], "football"),
    ("Fitness, Gym et Danse", NAVBAR_CATEGORIES[5], "pool2"),
    ("Loisirs", NAVBAR_CATEGORIES[6], "pool"),
    ("Autres", "", "dots")
))
