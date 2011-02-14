import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 6

USE_HTTPS = False # True

SESSION_COOKIE_DOMAIN = None # 'm.erentmarket.com'

CACHE_MIDDLEWARE_KEY_PREFIX = 'uk:mobile'

TEMPLATE_DIRS = (
    local_path('templates/mobile/uk/'),
    local_path('templates/mobile/'),
    local_path('templates/uk/'),
    local_path('templates/'),
)

MOBILE = True

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-uk'

AFFILIATE_TAG = 'uk'

GOOGLE_REGION_CODE = '.co.uk'

DEFAULT_SITES = [5, 6]
