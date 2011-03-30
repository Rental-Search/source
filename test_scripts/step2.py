from eloue.rent.models import Booking
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

sys.path.insert(0, "/Users/lin/work/eloue/")
sys.path.insert(0, "/Users/lin/work/eloue/eloue")

from django.core.management import setup_environ
from eloue import settings

setup_environ(settings)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)



def setup_env():
    import os
    from optparse import OptionParser

    usage = "usage: %prog -s SETTINGS | --settings=SETTINGS"
    parser = OptionParser(usage)
    parser.add_option('-s', '--settings', dest='settings', metavar='SETTINGS',
                      help="The Django settings module to use")
    (options, args) = parser.parse_args()
    if not options.settings:
        parser.error("You must specify a settings module")

    os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    
    
def process_booking(uuid):
    booking = Booking.objects.get(uuid=uuid)
    domain = Site.objects.get_current().domain
    protocol = "https" if USE_HTTPS else "http"
    booking.hold(
        cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
        return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
    )
    
    
if __name__=='__main__':
    setup_env()
    process_booking("e306879130994c1586287af2b9ac9c0d")