# -*- coding: utf-8 -*-
import re

from django.http import HttpResponsePermanentRedirect

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login, password_reset, password_reset_confirm, password_reset_confirm_uidb36, password_reset_done, password_reset_complete
from django.utils.html import strip_spaces_between_tags as compress_html
from django.utils.encoding import DjangoUnicodeDecodeError
from django.views.static import serve
from django.http.response import HttpResponseNotFound
from django.core.urlresolvers import resolve


class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response.get('Content-Type', ''):
            try:
                response.content = compress_html(response.content)
            except DjangoUnicodeDecodeError:
                pass
        return response


class RequireLoginMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        from accounts.views import authenticate, contact
        if request.user.is_authenticated():
            return None
        if view_func in [authenticate, serve, logout_then_login, password_reset, password_reset_confirm, password_reset_confirm_uidb36, password_reset_done, password_reset_complete, contact]:
            return None
        return login_required(view_func)(request, *view_args, **view_kwargs)


class UrlRedirectMiddleware:
    """
    This middleware lets you match a specific url and redirect the request to a
    new url.

    You keep a tuple of url regex pattern/url redirect tuples on your site
    settings, example:

    URL_REDIRECTS = (
        (r'www\.example\.com/hello/$', 'http://hello.example.com/'),
        (r'www\.example2\.com/$', 'http://www.example.com/example2/'),
    )

    """
    def process_request(self, request):
        host = request.META['HTTP_HOST']
        path = request.META['PATH_INFO']
        
        for url_pattern, redirect_domain in settings.URL_REDIRECTS:
            redirect_url = '%s%s' % (redirect_domain, path)
            regex = re.compile(url_pattern)
            if regex.match(host):
                return HttpResponsePermanentRedirect(redirect_url)
            
            
class StagingRestrictionMiddleware(object):    
    
    def process_request(self, request):
        if not (resolve(request.path_info).view_name == 'admin:index'
                 or request.user.is_superuser):
            return HttpResponseNotFound()
        
        
