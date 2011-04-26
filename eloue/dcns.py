import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 7

USE_HTTPS = False

SESSION_COOKIE_DOMAIN = None #'e-loue.dcnsgroup.com'

CACHE_MIDDLEWARE_KEY_PREFIX = 'dcns'

AFFILIATE_TAG = 'dcns'

LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'eloue.accounts.auth.PrivatePatronModelBackend',
)

MIDDLEWARE_CLASSES += ('eloue.middleware.RequireLoginMiddleware',)

DEFAULT_SITES = [7]

TEMPLATE_DIRS = (
    local_path('templates/dcns/'),
    local_path('templates/'),
)