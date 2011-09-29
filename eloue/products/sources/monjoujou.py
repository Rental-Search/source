from decimal import Decimal as D

from lxml import etree
import urllib2
import logbook
import feedparser

from . import BaseSource, Product
from content_extractor import id_gen

BASE_URL='http://www.monjoujou.com/'

log = logbook.Logger('eloue.rent.sources')

class SourceClass(BaseSource):
    
    id = id_gen()
    
    def get_prefix(self):
        return 'source.monjoujou'
    
    def get_docs(self):
        feed = feedparser.parse(BASE_URL + 'jouets.xml', agent='Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4')
        for entry in feed.entries:
            description_html = entry.description
            description_tree = etree.HTML(description_html)
            id_c = self.id.next()
            location = "France"
            lat, lon = BaseSource.get_location(self, location)
            thumbnail = description_tree[0][0][0].attrib['src']
            description = description_tree[0][1]
            yield Product({
                'id': '%s.%s' % (SourceClass().get_prefix(), id_c),
                'summary': '%s' % entry.title,
                'description': ' '.join([text.strip() for text in description.itertext(tag='p')]),
                'categories': ['eveil-et-jouets-bebe', 'jeux'],
                'lat': 0, 'lng': 0,
                'city': location,
                'price': D('0.66'),
                'owner': 'monjoujou',
                'owner_url': BASE_URL,
                'url': entry.link,
                'thumbnail': thumbnail,
                'django_id': '%s.%s' % (self.get_prefix(), id)
            })