import os

from eloue.settings import *
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 8

TIME_ZONE = 'Europe/Paris'


SESSION_COOKIE_DOMAIN = 'stockerentreparticuliers.com'

CACHE_MIDDLEWARE_KEY_PREFIX = 'sep'

ROOT_URLCONF = 'sep_urls'

USE_HTTPS = False

AFFILIATE_TAG = 'sep'

DEFAULT_SITES = [8]

TEMPLATE_DIRS = (
    local_path('templates/sep/'),
    local_path('templates/'),
)