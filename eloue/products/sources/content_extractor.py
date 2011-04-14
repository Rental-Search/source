import re
import logbook
from lxml import etree
from urllib import urlopen
from decimal import Decimal as D

log = logbook.Logger('eloue.rent.sources')

re_num = re.compile("[0-9]*\,?[0-9]+")

def __make_get_set_base_url():
    BASE_URL = [""]

    def get_base_url():
        return BASE_URL[0]

    def set_base_url(base_url):
        BASE_URL[0] = base_url

    return (get_base_url, set_base_url)

get_base_url, set_base_url = __make_get_set_base_url()

def html_tree(url):
    try:
        html_page = urlopen(get_base_url() + url)
        return etree.parse(html_page, etree.HTMLParser())
    except Exception, e:
        log.exception("Exception: %s".format(e))
        return

def tree_from_link(a):
    return html_tree(a.get("href"))

def follow_all(extractor, a_list):
    for a in a_list:
        href = a.get("href")
        tree = html_tree(href)
        if not tree: return
        for p in extractor(tree, href=href):
            yield p

def extract_price(string, sep=","):
    return D(re_num.findall(string)[0].replace(",", "."))

def id_gen():
    i = 1
    while True:
        i+=1
        yield i

