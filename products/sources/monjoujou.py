from decimal import Decimal as D

from lxml import etree
import logbook
import feedparser

from . import BaseSource, meta_class
from content_extractor import id_gen

BASE_URL='http://www.monjoujou.com/'

log = logbook.Logger('eloue.rent.sources')

class SourceClass(BaseSource):
    _meta = meta_class('sources', 'monjoujou')
    
    id = id_gen()
    
    def get_docs(self):
        feed = feedparser.parse(BASE_URL + 'jouets.xml', agent='Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4')
        location = 'France'
        #lat, lon = self.get_coordinates(location)
        for entry in feed.entries:
            description_html = entry.description
            description_tree = etree.HTML(description_html)
            c_id = self.id.next()
            thumbnail = description_tree[0][0][0].attrib['src']
            description = description_tree[0][1]
            yield self.make_product({
                'summary': '%s' % entry.title,
                'description': ' '.join([text.strip() for text in description.itertext(tag='p')]),
                'categories': ['eveil-et-jouets-bebe', 'jeux'],
                'location': '0,0',
                'city': location,
                'price': D('0.66'),
                'owner': 'monjoujou',
                'owner_url': BASE_URL,
                'url': entry.link,
                'thumbnail': thumbnail,
            }, pk=c_id)
