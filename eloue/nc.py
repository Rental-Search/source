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

TEMPLATE_DIRS = (
    local_path('templates/nc/'),
    local_path('templates/'),
)


DEFAULT_LOCATION = {
    'city': u'Noumea',
    'coordinates': (-22.29349, 166.463989),
    'country': u'Nouvelle-Caledonie',
    'fallback': None,
    'radius': 260.0,
    'region': None,
    'region_coords': None,
    'region_radius': None,
    'source': 4
}

INSURANCE_AVAILABLE = False
