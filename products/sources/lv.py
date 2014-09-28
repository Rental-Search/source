# -*- coding: utf-8 -*-
import tarfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from decimal import ROUND_CEILING, Decimal as D
from ftplib import FTP
from lxml import objectify, etree

from django.conf import settings
from . import BaseSource, meta_class

LV_FTP = getattr(settings, 'LV_FTP', "ftp.bo.location-et-vacances.com")
LV_FTP_USER = getattr(settings, 'LV_FTP_USER', "eloue")
LV_FTP_PASSWORD = getattr(settings, 'LV_FTP_PASSWORD', 'u1Pur-qh')


def get_tag(element, tag):
    return next(element.iterchildren(tag))

class SourceClass(BaseSource):
    _meta = meta_class('sources', 'lv')
    
    def get_archive(self):
        archive = StringIO()
        ftp = FTP(LV_FTP)
        ftp.login(LV_FTP_USER, LV_FTP_PASSWORD)
        ftp.retrbinary('RETR export_letv.tar.gz', archive.write)
        ftp.quit()
        archive.seek(0)
        return archive

    def get_product(self, element):
        descriptions = element.xpath('descriptions/lang[@iso="fr"]')
        if len(descriptions):
            description = "%s %s" % (get_tag(descriptions[0], "description_interieur").text, get_tag(descriptions[0], "description_exterieur"))
        else:
            description = get_tag(element, "nom_hergement").text
        photos = element.xpath('photos/photo')
        if photos:
            thumbnail = get_tag(get_tag(element, "photos"), "photo").text
        else:
            thumbnail = None
        if get_tag(element, "type_hebergement").text == 'Appartement':
            categories = ['lieu', 'appartement']
        elif get_tag(element, "type_hebergement").text == 'Maison':
            categories = ['lieu', 'maison-villa']
        else:
            categories = ['lieu']
        ville = get_tag(get_tag(element, "localisation"),"ville").text
        pays = get_tag(get_tag(element, "localisation"),"pays_libelle").text
        zip_code = get_tag(get_tag(element, "localisation"),"code_postal").text
        lat, lon = self.get_coordinates("%s %s" % (ville, pays))
        price = D(get_tag(element, "prix_mini").text) / D('7')
        yield self.make_product({
            'summary': get_tag(element, "nom_hergement").text,
            'description': description,
            'categories': categories,
            'location': '%s,%s' % (lon, lat),
            'city': ville, 'zipcode': zip_code,
            'price': price.quantize(D(".00"), rounding=ROUND_CEILING),
            'owner': 'location-et-vacances',
            'owner_url': 'http://www.location-et-vacances.com/',
            'url': "%s?cle=eloue" % get_tag(descriptions[0], "url_fiche").text,
            'thumbnail': thumbnail,
        }, pk=element.get('id'))
    
    def get_docs(self):
        tar = tarfile.open(fileobj=self.get_archive(), mode="r:gz")
        for member in tar:
            part = tar.extractfile(member)
            root = objectify.parse(part, parser=etree.XMLParser(recover=True))
            #gen = pool.imap(parse_doc, elements, 100)
            for element in root.xpath('//hebergement'):
                yield self.get_product(element)
