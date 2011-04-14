# -*- coding: utf-8 -*-
from . import BaseSource, Product
from collections import defaultdict
from content_extractor import *
import re

CATEGORIES = {
    "Chauffage": ["bricolage", "climatisation-et-chauffage"],
}

XP_CATEGORIES = "//div[@class='fl']/div[2]/h2/a"
XP_NEXTPAGE = "//div[contains(@class, 'pagination')]//div[@class='right']//a[@class='previous']"
XP_PRODUCT = "//div[contains(@class, 'produit')]//h3//a"
XP_PRICE = "//div[@class='texte']/p[@class='prix']/strong"
XP_PNAME = "//h2[@class='titre1']"
XP_PDESC = "//div[@id='desc']//div[@class='texte']"
XP_THUMBNAIL = "//div[@class='visuel']//img"

BASE_URL = "http://www.kiloutou.fr"

class SourceClass(BaseSource):

    id = id_gen()

    def __init__(self, *args, **kwargs):
        BaseSource.__init__(self, *args, **kwargs)
        set_base_url(BASE_URL)

    def get_categories(self, html_tree):
        for p in follow_all(self.get_products, html_tree.findall(XP_CATEGORIES)):
            yield p

    def get_products(self, html_tree, href=None):
        link_to_next = html_tree.xpath(XP_NEXTPAGE)[0]

        for p in follow_all(self.get_product, html_tree.xpath(XP_PRODUCT)):
            yield p

        for p in self.get_products(tree_from_link(link_to_next)):
            yield p

    def get_product(self, html_tree, href=None):
        if not href.startswith("/Location"):
            return

        cat, subcat = [s.replace("Location-","") for s in href.split("/")[2:4]]
        categories = CATEGORIES.get(cat, CATEGORIES.get(subcat, []))
        price_string = html_tree.find(XP_PRICE).text
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
            'thumbnail' : html_tree.find(XP_THUMBNAIL).attrib["src"],
            'django_id' : 'kiloutou.%d' % c_id
        })

    def get_prefix(self):
        return 'source.kiloutou'

    def get_docs(self):
        for product in self.get_categories(html_tree("/location-de-materiel")):
            yield product

