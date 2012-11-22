# -*- coding: utf-8 -*-
import re
import urllib
import urlparse
import random
import time, datetime

import redis

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.utils.html import strip_spaces_between_tags as compress_html
from django.utils.encoding import DjangoUnicodeDecodeError
from django.views.static import serve

from eloue.accounts.views import authenticate, contact

from eloue.http_user_agents import *

class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            try:
                response.content = compress_html(response.content)
            except DjangoUnicodeDecodeError:
                pass
        return response


class RequireLoginMiddleware(object):
	def process_view(self, request, view_func, view_args, view_kwargs):
		if request.user.is_authenticated():
			return None
		if view_func in [authenticate, serve, logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete, contact]:
			return None
		return login_required(view_func)(request, *view_args, **view_kwargs)
    

class SearchBotReportMiddleware(object):
    def process_request(self, request):
        var_cookie = 'UA-36530163-1'
        print request
        http_user_agent = request.META.get('HTTP_USER_AGENT', '')
        for http_user_agent_re in http_user_agents:
            if re.match(http_user_agent_re, http_user_agent):
                request_dict = {
                    'utmwv': 1,
                    'utmn': random.randint(1000000000,9999999999), #Nb au hasard
                    'utmsr': '', #Resolution ecran
                    'utmsc': '', #Qualite ecran
                    'utmul': '', #Langue du navigateur
                    'utmje': '0', #Java enabled
                    'utmfl': '', #Flash version
                    'utmdt': '', #Nom de la page visitée
                    'utmhn': 'e-loue.com', #Nom du site Web
                    'utmr': '', #pas de referer
                    'utmp': request.path, #Page Vue par le visiteur
                    'utme': '', #Nombre???(Objet*Action*Label) ': '> 5(Robots*Bot Name*Pathname)
                    'utmac': '', #Numero de compte analytics
                    'utmcc': '__utma%3D{var_cookie}.{var_random}.{var_now}.{var_now}.{var_now}.1%3B%2B''__utmb%3D{var_cookie}%3B%2B__utmc%3D{var_cookie}%3B%2B__utmz%3D{var_cookie}''.{var_now}.1.1.utmccn%3D(organic)%7Cutmcsr%3D{botname}%7Cutmctr%3D{uri}%7Cutmcmd%3Dorganic%3B%2B__utmv%3D{var_cookie}.Robot%20hostname%3A%20{var_server}%3B'.format(
                        var_cookie=var_cookie,
                        var_random=random.randint(1000000000,2000000000),
                        var_now=int(time.mktime(datetime.datetime.now().timetuple())),
                        botname=http_user_agents[http_user_agent_re],
                        uri=request.path,
                        var_server=request.META['REMOTE_HOST'],
                    )
                }
                print request_dict
                request_string = urllib.urlencode(request_dict)
                ping_url = urlparse.urlunparse(('http', 'www.google-analytics.com', '__utm.gif', None, request_string, None))
                r = redis.Redis(*settings.GA_PING_QUEUE_CONNECTION)
                r.lpush(settings.GA_PING_QUEUE_NAME, ping_url)
                break
        return None
