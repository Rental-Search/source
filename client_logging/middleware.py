from .views import LoggingRateThrottle

class ClientLoggingMiddleware(object):    
    
    def __init__(self):
        lrt = LoggingRateThrottle()
        self.num_requests = lrt.num_requests
        self.duration = lrt.duration 

    def process_response(self, request, response):
        if not request.COOKIES.get("eloue_el"):
            response.set_cookie("eloue_el", 
                                value=self.num_requests,
                                max_age=self.duration)
            response.set_cookie("eloue_ec", 
                                value=0,
                                max_age=self.duration)
        return response