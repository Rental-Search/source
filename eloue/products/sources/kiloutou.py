# -*- coding: utf-8 -*-
from . import BaseSource, Product
from decimal import Decimal as D
from collections import defaultdict
from itertools import chain
import re
import logbook
import urllib2
import lxml.html
from lxml import etree
import StringIO
import gzip
from content_extractor import id_gen
import contextlib

log = logbook.Logger('eloue.rent.sources')
CATEGORIES = {
    "Chauffage": ["bricolage", "climatisation-et-chauffage"],
}


XP_CATEGORIES=r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@id='page']/div[@class='panel-pane' and position()=2]/div[@class='' and position()=1]/div[@class='pane-content']/div[@id='nav']/div[@class='nav-inner']/ul[@class='menu']/li/div[@class='drop-down']/div[@class='mid' and position()=2]/ul[@class='menu']/li/a"
XP_NEXTPAGE=r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@class='product-page product-listing two-column' and @id='page']/div[@id='main-wrapper']/div[@class='main-inner' and position()=2]/div[@class='']/div[@class='pane-content']/div[@class='blocks-area' and position()=2]/div[@class='center' and position()=2]/div[@class='panel-pane']/div[@class='' and position()=3]/div[@class='pane-content']/div[@class='pager_container']/div[@class='item-list']/ul[@class='pager']/li[@class='pager-item']/a[@class='active']"
XP_PRODUCT=r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@class='product-page product-listing two-column' and @id='page']/div[@id='main-wrapper']/div[@class='main-inner' and position()=2]/div[@class='']/div[@class='pane-content']/div[@class='blocks-area' and position()=2]/div[@class='center' and position()=2]/div[@class='panel-pane']/div[@class='' and position()=1]/div[@class='pane-content']/div[@class='list' and @id='kt-center-results']/ul/li/div[@class='descrip']/h4/a"

XP_PRICE = r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@class='product-page product-listing two-column' and @id='page']/div[@id='main-wrapper']/div[@class='main-inner' and position()=2]/div[@class='']/div[@class='pane-content']/div[@class='product-info' and position()=1]/div[@class='right' and position()=3]/div[@class='panel-pane']/div[@class='']/div[@class='pane-content']/div[@class='price']/span[@class='current']/span[@class='point' and position()=1]"
XP_PNAME = r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@class='product-page product-listing two-column' and @id='page']/div[@id='main-wrapper']/div[@class='main-inner' and position()=2]/div[@class='']/div[@class='pane-content']/div[@class='product-info' and position()=1]/div[@class='panel-pane' and position()=1]/div[@class='']/div[@class='pane-content']/h2[@class='product-title']"
XP_PDESC = r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@class='product-page product-listing two-column' and @id='page']/div[@id='main-wrapper']/div[@class='main-inner' and position()=2]/div[@class='']/div[@class='pane-content']/div[@class='product-info' and position()=1]/div[@class='left' and position()=2]/div[@class='panel-pane']/div[@class='']/div[@class='pane-content']/div[@class='about' and position()=3]/div[@class='pour' and position()=1]"
XP_THUMBNAIL = r"/html/body/div[@class='particulier' and @id='page-wrapper']/div[@class='product-page product-listing two-column' and @id='page']/div[@id='main-wrapper']/div[@class='main-inner' and position()=2]/div[@class='']/div[@class='pane-content']/div[@class='product-info' and position()=1]/div[@class='left' and position()=2]/div[@class='panel-pane']/div[@class='']/div[@class='pane-content']/div[@class='pic-partager' and position()=2]/div[@class='gallery-block' and position()=1]/div[@class='main-image' and position()=1]/ul/li/a/img[@class='imagecache imagecache-product_main_photo']"

BASE_URL = "http://www.kiloutou.fr"

def req_builder(url):
    return urllib2.Request(url, 
      headers={
        'Referer': 'http://www.kiloutou.fr/e-demolition-day/',
        'Accept-encoding': 'none'
      })

def get_html_tree(req):
    try:
        with contextlib.closing(urllib2.urlopen(req, timeout=5)) as html_page:
            content = html_page.read()
            decompressed = gzip.GzipFile(fileobj=StringIO.StringIO(content)) if html_page.info().get('Content-Encoding') == 'gzip' else StringIO.StringIO(content)
            return etree.parse(decompressed, etree.HTMLParser())
    except Exception, e:
        log.exception("Exception: {0}".format(e))
        return

def follow_all(content_extractor, a_list):
    for a in a_list:
        url = BASE_URL + a.get('href')
        for content in content_extractor(get_html_tree(req_builder(url)), href=url):
            yield content

class SourceClass(BaseSource):

    id = id_gen()

    def __init__(self, *args, **kwargs):
        BaseSource.__init__(self, *args, **kwargs)

    def get_categories(self, html_tree, href=None):
        for p in follow_all(self.get_products, html_tree.xpath(XP_CATEGORIES)):
            yield p

    def get_products(self, html_tree, href=None, recursive=True):
        
        for p in follow_all(self.get_product, html_tree.xpath(XP_PRODUCT)):
            yield p
        
        if recursive:
            nodes_next = html_tree.xpath(XP_NEXTPAGE)
            for p in follow_all(lambda x, href=None: self.get_products(x, recursive=False, href=href), nodes_next):
                yield p



    def get_product(self, html_tree, href=None):
        c_id = self.id.next()
        location = "France"
        lat, lon = BaseSource.get_coordinates(self, location)
        yield Product({
            'id' : "%s.%d" % (self.get_prefix(), c_id),
            'summary' : html_tree.xpath(XP_PNAME)[0].text.strip(),
            'description' : html_tree.xpath(XP_PDESC)[0].text.strip(),
            'categories' : [],
            'lat' : lat, 'lng' : lon,
            'city' : location,
            'price' : None if html_tree.xpath(XP_PRICE)[0].text.strip() == "Sur devis" else D(html_tree.xpath(XP_PRICE)[0].text.strip()),
            'owner' : 'kiloutou',
            'owner_url' : BASE_URL + "/",
            'url' : href,
            'thumbnail' : html_tree.xpath(XP_THUMBNAIL)[0].attrib["src"],
            'django_id' : 'kiloutou.%d' % c_id
        })


    def get_prefix(self):
        return 'source.kiloutou'

    def get_docs(self):
        for product in self.get_categories(get_html_tree(req_builder(BASE_URL))):
            yield product

