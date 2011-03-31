from eloue.rent.models import Booking
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from eloue import settings

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


def get_status(uuid):
    booking = Booking.objects.get(uuid=uuid)
    return booking.state

def process_booking_step_one(uuid):
    """
    state authorizing -> authorized -> pending
    """
    booking = Booking.objects.get(uuid=uuid)
    booking.state = Booking.STATE.AUTHORIZED # authorizing -> authorized ::preapproval, preapproval_ipn
    booking.send_ask_email()
    booking.save()
    #booking.state = Booking.STATE.PENDING #ipn ignored, authorized -> pending ::booking_accept
    #booking.send_acceptation_email()
    #booking.save()
    
def process_booking_step_two(uuid):
    """
    state pending -> ongoing
    """
    booking = Booking.objects.get(uuid=uuid)
    domain = Site.objects.get_current().domain
    protocol = "https" if USE_HTTPS else "http" # ::command ongoing, hold, pay_ipn
    booking.hold(
        cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
        return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
    )
    booking.state = Booking.STATE.ONGOING 
    booking.save()
    

def process_booking_step_three(uuid):
    """
    state ongoing -> ended
    """
    booking = Booking.objects.get(uuid=uuid) # ::command ended
    booking.state = Booking.STATE.ENDED
    booking.send_ended_email()
    booking.save()
    

def process_booking_step_four(uuid):
    """
    state ended -> closing
    """
    booking = Booking.objects.get(uuid=uuid)
    booking.pay() #ended -> closing, time ignored ::pay
    booking.send_closed_email()

def process_booking_step_five(uuid):
    """
    closing -> closed
    """
    booking = Booking.objects.get(uuid=uuid) 
    booking.state = Booking.STATE.CLOSED #ipn ignored, closing -> closed ::pay_ipn
    booking.save()
    
def test_httplib(uuid):
    """
    import httplib, urllib
    ELOUE_URL = "192.168.0.28:8000"
    params = urllib.urlencode({"booking_pk": uuid})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(ELOUE_URL) 
    conn.request("POST", '/booking/ipn/fakepreapproval', params, headers)
    response = conn.getresponse()
    conn.close()
    print "###### http close #######"
    """
    import urllib2
    theurl = "http://192.168.0.28:8000/booking/ipn/fakepreapproval/?booking_pk=%s"%uuid
    req = urllib2.Request(url=theurl)
    f = urllib2.urlopen(req)
    print f.read()

if __name__=='__main__':
    #setup_env()
    process_booking("e306879130994c1586287af2b9ac9c0d")
    
    
    
    
    
    