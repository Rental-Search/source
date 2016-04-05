from .serializers import LogEntrySerializer
from rest_framework.parsers import JSONParser
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from eloue.api.viewsets import SimpleViewSet
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.conf import settings
from util import log_stacktrace


class LoggingRateThrottle(UserRateThrottle):
    rate = settings.CLIENT_EXCEPTION_RATE
    

class ClientLogViewSet(SimpleViewSet):
    
    throttle_classes = [LoggingRateThrottle, ]
    parser_classes = [JSONParser, ]
    renderer_classes = [JSONRenderer, ]
        
    public_actions = ('log', )
        
    def log(self, request):
        
        les = LogEntrySerializer(data=request.DATA)
        
        if les.is_valid():
            
            les.data.update(
                            {"session_key": request.session.session_key or "undefined",
                            "user_agent": request.META['HTTP_USER_AGENT'] or "undefined",
                            "ec": request.COOKIES.get('eloue_ec', 0),
                            "rate_limit": request.COOKIES.get('rate_limit', 
                                                              settings.CLIENT_EXCEPTION_RATE),})
            
            log_stacktrace(les.data)
        
        return Response(status=status.HTTP_201_CREATED)
    
        