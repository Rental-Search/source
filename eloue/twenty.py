import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


SITE_ID = 2

USE_HTTPS = True

SESSION_COOKIE_DOMAIN = 'eloue.20minutes.fr'

AFFILIATE_TAG = '20m'

TEMPLATE_DIRS = (
    local_path('templates/20minutes/'),
    local_path('templates/'),
) 