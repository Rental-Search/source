import logging
from logbook import handlers #TODO verify if this is OK without try-catch

CHANNEL = u"javascript"
LOG_MESSAGE = u"exception"
USER_DATA = u"||| {user_agent} ||| {session_key} ||| {ec}/{rate_limit} |||"
FRAME_FORMAT = u" {functionName}({args})@{fileName}:{lineNumber}:{columnNumber}" 

logger = logging.getLogger(CHANNEL)    
    
def format_frame(frame):
    return FRAME_FORMAT.format(**frame)


def format_record(fs, record):
    frames = list(map(format_frame, record.extra['stack']))
    frames[0] = fs.format(record=record) + " " + USER_DATA.format(**record.extra) + frames[0]
    return u"\n".join(frames)


def js_error_log_filter(record, handler):
    return record.channel == CHANNEL
    
def js_error_formatter_syslog(record, handler):
    return format_record(handlers.SYSLOG_FORMAT_STRING, record)
    
def js_error_formatter_stderr(record, handler):
    return format_record(handlers.DEFAULT_FORMAT_STRING, record)

def log_stacktrace(stacktrace):
    logger.info(LOG_MESSAGE, extra=stacktrace)