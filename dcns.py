# -*- coding: utf-8 -*-
import sys, site, os
local_path = lambda path: os.path.join(os.path.abspath(os.path.dirname(__file__)), path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'eloue.dcns'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAJ3PXVVKSTM3WSZSQ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

site.addsitedir(local_path('env/lib/python2.6/site-packages'))

sys.path.insert(0, local_path('.'))
sys.path.insert(0, local_path('eloue'))
sys.path.insert(0, local_path('env/lib/python2.6/site-packages'))

import django.core.handlers.wsgi
from haystack import site
application = django.core.handlers.wsgi.WSGIHandler()
