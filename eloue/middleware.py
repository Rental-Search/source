# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.utils.html import strip_spaces_between_tags as compress_html
from django.utils.encoding import DjangoUnicodeDecodeError
from django.views.static import serve

from eloue.accounts.views import authenticate
from eloue.products.views import homepage


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
		print request.user.is_authenticated()
		if request.user.is_authenticated():
			print request.user.is_authenticated()
			return None
		if view_func in [homepage, authenticate, serve, logout_then_login, password_reset, password_reset_confirm, password_reset_done, password_reset_complete ]:
			return None
		return login_required(view_func)(request, *view_args, **view_kwargs)
    
