import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 5

USE_HTTPS = False

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-uk'

SESSION_COOKIE_DOMAIN = 'e-loue.uk'

CACHE_MIDDLEWARE_KEY_PREFIX = 'uk'

AFFILIATE_TAG = 'uk'

GOOGLE_REGION_CODE = '.co.uk'

DEFAULT_SITES = [5, 6]

TEMPLATE_DIRS = (
    local_path('templates/uk/'),
    local_path('templates/'),
)
