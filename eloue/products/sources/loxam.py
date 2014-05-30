from . import BaseSource, meta_class
import contextlib
import urllib2
from content_extractor import id_gen
from lxml import etree
import re
import logbook
import gzip
import io

log = logbook.Logger('eloue.rent.sources')

CATEGORIES = {}

XP_CATEGORIES = './/div[@class="main-menu-td"]/div[@class="menu-dyn"]/table/tr/td[2]/ul/li/em[@class="loc-item"]/a'
XP_PAGES = ".//*[@id='toolbar']/table/tr/td/a"

XP_PRODUCT = ".//*[@id='content']/table/tr/td/div/strong/a[1]"

XP_SUMMARY = ".//*[@id='caddy']/h1"
XP_PRICE = ".//*[@id='bloc-tarifs-part']/table/tr[2]/td[1]/table/tr[1]/td[2]"
XP_DESC = ".//*[@id='bonasavoir']/tr[2]/td/div"
XP_DESC2 = ".//form[@id='caddy']//div[@class='descr']/div/p"
XP_THUMBNAIL = ".//*[@id='caddy']/img"

BASE_URL = "http://www.loxam.fr"


def html_tree(url):
    try:
        urll = BASE_URL + url
        with contextlib.closing(urllib2.urlopen(urll, timeout=5)) as html_page:
            return etree.parse(html_page, etree.HTMLParser(recover=True, encoding='utf-8'))
    except Exception, e:
        log.exception("Exception: {0}".format(e))
        return

def tree_from_link(a):
    return html_tree(a.get("href"))

def follow_all(extractor, a_list, pages=False):
    for a in a_list:
        href = a.get("href")
        tree = html_tree(href)
        if not tree: return
        for p in extractor(tree, href=href, pages=pages):
            yield p

def extract_price(string, sep=","):
    from decimal import Decimal as D
    re_num = re.compile("[0-9]*\,?[0-9]+")
    return D(re_num.findall(string)[0].replace(",", "."))

class SourceClass(BaseSource):
    _meta = meta_class('sources', 'loxam')

    id = id_gen()

    def __init__(self, *args, **kwargs):
        BaseSource.__init__(self, *args, **kwargs)
    
    def _html_loader(self, url):
        while True:
            try:
                with contextlib.closing(urllib2.urlopen(url, timeout=5)) as response:
                    if response.info().get('Content-Encoding') is 'gzip':
                        response = gzip.GzipFile(fileobj=io.BytesIO(response))
                    return etree.parse(response, etree.HTMLParser(recover=True, encoding='utf-8'))
            except urllib2.URLError:
                continue
            else:
                break
        
    def get_categories(self, url):
        html_tree = self._html_loader(url)
        for atag in html_tree.xpath(XP_CATEGORIES):
            href = atag.get('href')
            for product in self.get_products(BASE_URL+href, pages=True):
                yield product

    def get_products(self, url, pages=False):
        html_tree = self._html_loader(url)
        for atag in html_tree.xpath(XP_PRODUCT):
            href = atag.get('href')
            product = self.get_product(BASE_URL+href)
            yield product
        if pages:
            for atag in html_tree.xpath(XP_PAGES):
                href = atag.get('href')
                for product in self.get_products(url+href):
                    yield product

    def get_product(self, url):
        html_tree = self._html_loader(url)
        cat, subcat = url.split("/")[2:4]
        subcat=subcat.replace("location-","")
        #if not (href.startswith("/location") and href.endswith(".html")): 
        #    return
        try:
            c_id = self.id.next()
            thumb_tree = html_tree.xpath(XP_THUMBNAIL)
            thumbnail = thumb_tree[0].attrib["src"] if len(thumb_tree) else ""
            description = ''.join([i.strip() for i in html_tree.find(XP_DESC).itertext()]) if html_tree.find(XP_DESC) is not None else ''.join(html_tree.find(XP_DESC2).itertext()) if html_tree.find(XP_DESC2) is not None else ''
            location = "France"
            lat, lon = self.get_coordinates(location)
            return self.make_product({
                'summary': html_tree.find(XP_SUMMARY).text,
                'description': description,
                'categories': CATEGORIES.get(cat, CATEGORIES.get(subcat, [])),
                'location': '%s,%s' % (lon, lat),
                'city' : location,
                'price': extract_price(html_tree.find(XP_PRICE).text),
                'owner' : 'loxam',
                'owner_url' : BASE_URL + "/",
                'url' : url,
                'thumbnail' : BASE_URL + thumbnail,
            }, pk=c_id)
        except Exception, e:
            log.exception("Exception : {0}".format(e))

    def get_docs(self):
        for product in self.get_categories(BASE_URL+"/"):
            yield product
