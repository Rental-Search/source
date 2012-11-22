from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import urllib2, contextlib

import redis
class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        r = redis.Redis(*settings.GA_PING_QUEUE_CONNECTION)
        while True:
            url = r.lpop(settings.GA_PING_QUEUE_NAME)
            if url is None:
                break
            try:
                with contextlib.closing(urllib2.urlopen(url)) as response:
                    print 'Hitting url %s' % url
                    if response.getcode() != 200:
                        print 'Error with url %s. Retrying.' % url
                        r.lpush(settings.GA_PING_QUEUE_NAME, ping_url)
            except (urllib2.HTTPError, urllib2.URLError):
                print 'Error with url %s. Retrying.' % url
                r.lpush(settings.GA_PING_QUEUE_NAME, ping_url)
