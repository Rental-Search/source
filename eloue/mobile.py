import os

from eloue.settings import *

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

SITE_ID = 3

TEMPLATE_DIRS = (
    local_path('templates/mobile/'),
    local_path('templates/'),
)

MOBILE = True