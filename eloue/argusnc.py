import os

from eloue.settings import *
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 10

SESSION_COOKIE_DOMAIN = 'locations.argus.nc'


USE_HTTPS = True

CACHE_MIDDLEWARE_KEY_PREFIX = 'argusnc'

AFFILIATE_TAG = 'argusnc'

GOOGLE_REGION_CODE = 'nc'

CONVERT_XPF = True

DEFAULT_SITES = [10]

TEMPLATE_DIRS = (
    local_path('templates/argusnc/'),
    local_path('templates/'),
)
