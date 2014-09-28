from decimal import Decimal as D

from . import BaseSource, meta_class
from content_extractor import html_tree
from lxml import etree
from urllib2 import urlopen
import logbook


BASE_URL="http://www.chronobook.fr/"

XP_DESC1="/html/body/div[@class='global' and position()=1]/div[@class='contenu' and position()=5]/div[@class='principal' and position()=2]/div[@class='redactionnel' and position()=3]/div[@class='section sectionAvecNav' and position()=2]/div[@class='fichelivre']/p[1]"
XP_DESC2="/html/body/div[@class='global' and position()=1]/div[@class='contenu' and position()=5]/div[@class='principal' and position()=2]/div[@class='redactionnel' and position()=3]/div[@class='section sectionAvecNav' and position()=2]/div[@class='fichelivre']/div[3]/p"

XP_IMAGE="/html/body/div[@class='global' and position()=1]/div[@class='contenu' and position()=5]/div[@class='principal'\
        and position()=2]/div[@class='redactionnel' and position()=3]/div[@class='section sectionAvecNav'\
        and position()=2]/div[@class='fichelivre']/a[2]/img[@class='couv']"

log = logbook.Logger('eloue.rent.sources')



class SourceClass(BaseSource):
    _meta = meta_class('sources', 'chronobook')
    
    def get_docs(self):
        try:
            xml_source = urlopen(BASE_URL + "xmlchronobook.php", timeout=5)
            books = etree.parse(xml_source, parser=etree.XMLParser(recover=True))
        except Exception, e:
            log.exception("Exception: %s".format(e))
        location = "Paris, France"
        lat, lon = self.get_coordinates(location)
        for book in books.getroot():
            attrib = book.attrib
            html = html_tree(attrib['fiche'])
            thumbnail = html.xpath(XP_IMAGE)
            if not len(thumbnail):
                continue
            else:
                thumbnail = html.xpath(XP_IMAGE)[0].attrib['src']
            description = ("\n".join([i.strip() for i in html.xpath(XP_DESC1)[0].itertext()])) if len(html.xpath(XP_DESC1)) else (("\n".join([i.strip() for i in html.xpath(XP_DESC2)[0].itertext()]) if len(html.xpath(XP_DESC2)) else ""))
            yield self.make_product({
                'summary': '%(author)s: %(title)s' % {'author': attrib['auteur'], 'title': book.text},
                'description': description,
                'categories': ['culture', 'livre'],
                'location': '%s,%s' % (lon, lat),
                'city': location,
                'price': D('0.45'),
                'owner': 'chronobook',
                'owner_url': BASE_URL,
                'url': attrib['fiche'],
                'thumbnail': BASE_URL+thumbnail,
            }, pk=attrib['id'])
