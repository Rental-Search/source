import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


SITE_ID = 7

USE_HTTPS = False

SESSION_COOKIE_DOMAIN = 'e-loue.dcnsgroup.com'

CACHE_MIDDLEWARE_KEY_PREFIX = 'dcns'

AFFILIATE_TAG = 'dcns'

TEMPLATE_DIRS = (
    local_path('templates/dcns/'),
    local_path('templates/'),
)