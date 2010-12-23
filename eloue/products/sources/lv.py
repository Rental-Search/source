# -*- coding: utf-8 -*-
import tarfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from decimal import ROUND_CEILING, Decimal as D
from ftplib import FTP
from lxml import objectify

from django.conf import settings

from . import BaseSource, Product

LV_FTP = getattr(settings, 'LV_FTP', "ftp.bo.location-et-vacances.com")
LV_FTP_USER = getattr(settings, 'LV_FTP_USER', "eloue")
LV_FTP_PASSWORD = getattr(settings, 'LV_FTP_PASSWORD', 'u1Pur-qh')


def parse_doc(element):
    descriptions = element.xpath('descriptions/lang[@iso="fr"]')
    if descriptions:
        description = "%s %s" % (descriptions[0].description_interieur.pyval, descriptions[0].description_exterieur.pyval)
    else:
        description = element.nom_hergement.pyval
    photos = element.xpath('photos/photo')
    if photos:
        thumbnail = element.photos.photo.pyval
    else:
        thumbnail = None
    if element.type_hebergement.pyval == 'Appartement':
        categories = ['lieu', 'appartement']
    elif element.type_hebergement.pyval == 'Maison':
        categories = ['lieu', 'maison-villa']
    else:
        categories = ['lieu']
    lat, lon = BaseSource().get_coordinates("%s %s" % (element.localisation.ville, element.localisation.pays_libelle))
    price = D(str(element.prix_mini.pyval)) / D('7')
    return Product({
        'id': '%s.%s' % (SourceClass().get_prefix(), element.get('id')),
        'summary': element.nom_hergement.pyval,
        'description': description,
        'categories': categories,
        'lat': lat, 'lng': lon,
        'city': element.localisation.ville.pyval, 'zipcode': element.localisation.code_postal.pyval,
        'price': price.quantize(D(".00"), rounding=ROUND_CEILING),
        'owner': 'location-et-vacances',
        'owner_url': 'http://www.location-et-vacances.com/',
        'url': "%s?cle=eloue" % element.descriptions.lang.url_fiche.pyval,
        'thumbnail': thumbnail,
        'django_id': 'lv.%s' % element.get('id'),
    })


class SourceClass(BaseSource):
    def get_prefix(self):
        return 'sources.lv'
    
    def get_archive(self):
        archive = StringIO()
        ftp = FTP(LV_FTP)
        ftp.login(LV_FTP_USER, LV_FTP_PASSWORD)
        ftp.retrbinary('RETR export_letv.tar.gz', archive.write)
        ftp.quit()
        archive.seek(0)
        return archive
    
    def get_docs(self):
        tar = tarfile.open(fileobj=self.get_archive(), mode="r:gz")
        pool, docs = self.get_pool(), []
        for member in tar:
            part = tar.extractfile(member)
            root = objectify.parse(part)
            elements = root.xpath('//hebergement')
            docs.extend(pool.map(parse_doc, elements, len(elements) // SourceClass.processes))
        pool.close()
        pool.join()
        return docs
    
