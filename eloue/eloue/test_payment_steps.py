from rent.models import Booking
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from eloue import settings

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


def get_status(uuid):
    booking = Booking.objects.get(uuid=uuid)
    return booking.state

def process_booking_step_one(uuid):
    """
    state authorizing -> authorized -> pending, not needed to test non-payment
    """
    booking = Booking.objects.get(uuid=uuid)
    booking.state = Booking.STATE.AUTHORIZED # authorizing -> authorized ::preapproval, preapproval_ipn
    booking.send_ask_email()
    booking.save()
    
def process_booking_step_two(uuid):
    """
    state pending -> ongoing, as time passed (time control), needed for test non-payment
    """
    booking = Booking.objects.get(uuid=uuid)
    booking.init_payment_processor()
    domain = Site.objects.get_current().domain
    protocol = "https" if USE_HTTPS else "http" # ::command ongoing, hold, pay_ipn to be ignored by nonpay
    booking.hold(
        cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
        return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
    )
    booking.state = Booking.STATE.ONGOING
    booking.save()

def process_booking_step_three(uuid):
    """
    state ongoing -> ended, as time passed (time control), needed for test non-payment
    """
    booking = Booking.objects.get(uuid=uuid) # ::command ended
    booking.state = Booking.STATE.ENDED
    booking.send_ended_email()
    booking.save()
    

def process_booking_step_four(uuid):
    """
    closing -> closed
    Attention, no need step four, so step five turn to be step four. not needed to test non-payment
    """
    booking = Booking.objects.get(uuid=uuid) 
    booking.state = Booking.STATE.CLOSED #ipn ignored, closing -> closed ::pay_ipn
    booking.save()
    
def httplib(uuid):
    
    import urllib2
    theurl = "http://192.168.0.28:8000/booking/ipn/fakepreapproval/?booking_pk=%s"%uuid
    req = urllib2.Request(url=theurl)
    f = urllib2.urlopen(req)


    
    
    
    
    
    