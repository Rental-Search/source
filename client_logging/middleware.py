
from django.conf import settings

class ClientLoggingMiddleware(object):    
    def process_response(self, request, response):
        response.set_cookie("eloue_el", settings.EXCEPTIONS_PER_SESSION)
        return response