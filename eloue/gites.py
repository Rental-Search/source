import os

from eloue.settings import *
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 12

SESSION_COOKIE_DOMAIN = 'locations.bienmeloger.nc'


USE_HTTPS = True

CACHE_MIDDLEWARE_KEY_PREFIX = 'gites'

AFFILIATE_TAG = 'gites'

GOOGLE_REGION_CODE = 'gites'

CONVERT_XPF = True

DEFAULT_SITES = [12]

TEMPLATE_DIRS = (
    local_path('templates/gites/'),
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
