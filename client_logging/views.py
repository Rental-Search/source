from .serializers import LogEntrySerializer
from rest_framework.parsers import JSONParser
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from eloue.api.viewsets import SimpleViewSet
from rest_framework.renderers import JSONRenderer
from rest_framework import status
import logging
from logging import Formatter
from django.template.base import Template
from logbook import handlers #TODO verify if this is OK without try-catch
from django.conf import settings


CHANNEL = u"javascript"
LOG_MESSAGE = u"exception"
FRAME_FORMAT = u" in {functionName}({args})@{fileName}:{lineNumber}:{columnNumber}" 


logger = logging.getLogger(CHANNEL)
    
    
def format_frame(frame):
    return FRAME_FORMAT.format(**frame)


def format_record(fs, record):
    frames = list(map(format_frame, record.extra['stack']))
    frames[0] = fs.format(record=record) + frames[0]
    return u"\n".join(frames)


def js_error_log_filter(record, handler):
    return record.channel == CHANNEL
    
def js_error_formatter_syslog(record, handler):
    return format_record(handlers.SYSLOG_FORMAT_STRING, record)
    
def js_error_formatter_stderr(record, handler):
    return format_record(handlers.DEFAULT_FORMAT_STRING, record)

def log_stacktrace(stacktrace):
    logger.info(LOG_MESSAGE, extra=stacktrace)


class LoggingRateThrottle(UserRateThrottle):
    rate = "60/hour" #TODO add rate from config


class ClientLogViewSet(SimpleViewSet):
    
    throttle_classes = [LoggingRateThrottle, ]
    parser_classes = [JSONParser, ]
    renderer_classes = [JSONRenderer, ]
        
    public_actions = ('log', )
        
    def log(self, request):
        
        les = LogEntrySerializer(data=request.DATA)
        
        if les.is_valid():
            log_stacktrace(les.data)
        
        return Response(les.data, status=status.HTTP_201_CREATED)
    
        