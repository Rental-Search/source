from . import BaseSource, Product
from content_extractor import *
import re

CATEGORIES = {}

XP_CATEGORIES = "//a[@class='onglet_lv_item']"
XP_SUBCAT = "//table//tr/td[2]//a[@class='location_rub_liste']"
XP_PRODUCT = "//table[3]//td[contains(@class, 'tableau_location_ligne') and position()=2]//a[1]"
XP_PRICE = "//table//tr[1]/td[@class='location_detail_prix']"
XP_DESC = "//td[@height=160]/div"
XP_THUMBNAIL = "//td[@id='maincontent_0']//table[2]//tr[3]/td/img"

BASE_URL = "http://www.loxam.fr/"

class SourceClass(BaseSource):

    set_base_url(BASE_URL)
    id = id_gen()

    def __init__(self, *args, **kwargs):
        BaseSource.__init__(self, *args, **kwargs)
        set_base_url(BASE_URL)

    def get_categories(self, html_tree):
        for p in follow_all(self.get_subcat,
                            html_tree.findall(XP_CATEGORIES)):
            yield p

    def get_subcat(self, html_tree, href=None):
        for p in follow_all(self.get_products, html_tree.findall(XP_SUBCAT)):
            yield p

    def get_products(self, html_tree, href=None):
        for p in follow_all(self.get_product, html_tree.xpath(XP_PRODUCT)):
            yield p

    def get_product(self, html_tree, href=None):
        cat, subcat = href.split("/")[2:4]
        subcat=subcat.replace("location-","")
        if not href.endswith(".html"): return
        try:
            c_id = self.id.next()
            thumb_tree = html_tree.xpath(XP_THUMBNAIL)
            thumbnail = thumb_tree[0].attrib["src"] if len(thumb_tree) else ""
            yield Product({
                'id' : "%s.%d" % (self.get_prefix(), c_id),
                'summary':  html_tree.findall("//h1")[1].text.split(":")[-1].strip(),
                'description': "\n".join([i.strip() for i in html_tree.xpath(XP_DESC)[0].itertext()]),
                'categories': CATEGORIES.get(cat, CATEGORIES.get(subcat, [])),
                'lat' : 0, 'lng' : 0,
                'city' : 'Paris',
                'price': extract_price(html_tree.find(XP_PRICE).text),
                'owner' : 'kiloutou',
                'owner_url' : BASE_URL + "/",
                'url' : BASE_URL + href,
                'thumbnail' : thumbnail,
                'django_id' : 'loxam.%d' % c_id
            })
        except Exception, e:
            pass

    def get_prefix(self):
        return 'source.loxam'

    def get_docs(self):
        for product in self.get_categories(html_tree("/")):
            yield product

