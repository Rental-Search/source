# -*- coding: utf-8 -*-
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eloue.settings")
#os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAJ3PXVVKSTM3WSZSQ'
#os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

from django.core.wsgi import get_wsgi_application
from dj_static import Cling

application = Cling(get_wsgi_application())
