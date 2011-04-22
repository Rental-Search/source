import os

from eloue.settings import *
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 4

SESSION_COOKIE_DOMAIN = 'e-loue.nc'


USE_HTTPS = False

CACHE_MIDDLEWARE_KEY_PREFIX = 'nc'

AFFILIATE_TAG = 'nc'

GOOGLE_REGION_CODE = 'nc'

CONVERT_XPF = True

DEFAULT_SITES = [4]

TEMPLATE_DIRS = (
    local_path('templates/nc/'),
    local_path('templates/'),
)
