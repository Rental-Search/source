# -*- coding: utf-8 -*-
from . import BaseSource, Product
from collections import defaultdict
from content_extractor import *
import re
import logbook

log = logbook.Logger('eloue.rent.sources')
CATEGORIES = {
    "Chauffage": ["bricolage", "climatisation-et-chauffage"],
}

XP_CATEGORIES = "//div[@class='fl']/div[2]/h2/a"
XP_NEXTPAGE = "//div[contains(@class, 'pagination')]//div[@class='right']//a[@class='previous' and position() = last()]"
XP_PRODUCT = "//div[contains(@class, 'produit')]//h3//a"
XP_PRICE = "//div[@class='texte']/p[@class='prix']/strong"
XP_PNAME = "//h2[@class='titre1']"
XP_PDESC = "//div[@id='desc']//div[@class='texte']"
XP_THUMBNAIL = "//div[@class='visuel']//img"

BASE_URL = "http://www.kiloutou.fr"
IMAGE_URL =  "http://filer.kiloutou.fr"
class SourceClass(BaseSource):

    id = id_gen()

    def __init__(self, *args, **kwargs):
        BaseSource.__init__(self, *args, **kwargs)

    def get_categories(self, html_tree):
        for p in follow_all(self.get_products, html_tree.findall(XP_CATEGORIES)):
            yield p

    def get_products(self, html_tree, href=None):

        for p in follow_all(self.get_product, html_tree.xpath(XP_PRODUCT)):
            yield p

        nodes_next = html_tree.xpath(XP_NEXTPAGE)
        if len(nodes_next):
            link_to_next = nodes_next[0]
            for p in self.get_products(tree_from_link(link_to_next)):
                yield p



    def get_product(self, html_tree, href=None):
        if not href.startswith("/Location"):
            return

        try:
            cat, subcat = [s.replace("Location-","") for s in href.split("/")[2:4]]
            categories = CATEGORIES.get(cat, CATEGORIES.get(subcat, []))
            if html_tree.find(XP_PRICE) is not None:
                price_string = html_tree.find(XP_PRICE).text
            else: return
            c_id = self.id.next()

            yield Product({
                'id' : "%s.%d" % (self.get_prefix(), c_id),
                'summary' : html_tree.find(XP_PNAME).text.strip(),
                'description' : "".join([t.strip() for t in html_tree.find(XP_PDESC).itertext()]),
                'categories' : categories,
                'lat' : 0, 'lng' : 0,
                'city' : 'Paris',
                'price' : extract_price(price_string),
                'owner' : 'kiloutou',
                'owner_url' : BASE_URL + "/",
                'url' : BASE_URL + href,
                'thumbnail' : IMAGE_URL + html_tree.find(XP_THUMBNAIL).attrib["src"][6:],
                'django_id' : 'kiloutou.%d' % c_id
            })
        except Exception, e:
            log.exception(e)

    def get_prefix(self):
        return 'source.kiloutou'

    def get_docs(self):
        set_base_url(BASE_URL)
        for product in self.get_categories(html_tree("/location-de-materiel")):
            yield product

