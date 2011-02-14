import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 5

USE_HTTPS = False # True

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-gb'

SESSION_COOKIE_DOMAIN = None # 'erentmarket.com'

CACHE_MIDDLEWARE_KEY_PREFIX = 'uk'

AFFILIATE_TAG = 'uk'

GOOGLE_REGION_CODE = '.co.uk'

DEFAULT_SITES = [5, 6]

TEMPLATE_DIRS = (
    local_path('templates/uk/'),
    local_path('templates/'),
)

MOBILE_REDIRECT_BASE = 'https://m.erentmarket.com'
