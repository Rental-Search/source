import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 9

USE_HTTPS = False

SESSION_COOKIE_DOMAIN = None #'shiseido.e-loue.com'

CACHE_MIDDLEWARE_KEY_PREFIX = 'shiseido'

COMMISSION = 0.10  # Our commission percentage

AFFILIATE_TAG = 'shiseido'

LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'eloue.accounts.auth.PrivatePatronModelBackend',
)

#MIDDLEWARE_CLASSES += ('eloue.middleware.RequireLoginMiddleware',)

DEFAULT_SITES = [9]

TEMPLATE_DIRS = (
    local_path('templates/shiseido/'),
    local_path('templates/'),
)