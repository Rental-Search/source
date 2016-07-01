# -*- coding: utf-8 -*-
from eloue.settings import *

SITE_ID = 13

CACHE_MIDDLEWARE_KEY_PREFIX = 'gosport'

for key in PIPELINE_JS:
    output_filename = PIPELINE_JS[key]['output_filename'].replace(
            '.js', '_%s.js' % "gosport")
    PIPELINE_JS[key]['output_filename'] = output_filename

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
    (("Sports d'hiver", NAVBAR_CATEGORIES[0], "ski"),
    ("Sports de raquette", NAVBAR_CATEGORIES[1], "tennis"),
    ("Cycles", NAVBAR_CATEGORIES[2], "bike"),
    ("Sports d'extérieur", NAVBAR_CATEGORIES[3], "golf")),
    (("Sports d'équipe", NAVBAR_CATEGORIES[4], "football"),
    ("Fitness, Gym et Danse", NAVBAR_CATEGORIES[5], "pool2"),
    ("Loisirs", NAVBAR_CATEGORIES[6], "pool"),
    ("Autres", "", "dots"))
))

DASHBOARD_REDIRECT_DOMAIN = env('DASHBOARD_REDIRECT_DOMAIN', 'www.e-loue.com')

URL_REDIRECTS = (
        (r'www\.go-sport-location\.com$', 'https://location.go-sport.com'),
        (r'www\.go-sport-location\.fr$', 'https://location.go-sport.com'),
        (r'www\.gosportlocation\.fr$', 'https://location.go-sport.com'),
        (r'gosportlocation\.com$', 'https://location.go-sport.com'),
        (r'www\.gosportlocation\.com$', 'https://location.go-sport.com'),
        (r'go-sport-location\.fr$', 'https://location.go-sport.com'),
        (r'gosportlocation\.fr$', 'https://location.go-sport.com'),
        (r'go-sport-location\.com$', 'https://location.go-sport.com'),
    )

MIDDLEWARE_CLASSES = (
    'eloue.middleware.UrlRedirectMiddleware',
    'sslify.middleware.SSLifyMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'eloue.middleware.SpacelessMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ANALYTICS.update({
                  'GOOGLE_ID': 'UA-58724631-1',
                  'SEGMENT_ID': 'i88y9ipduvQyXRW63WiC9XeAWORuTxTa',
                  })
