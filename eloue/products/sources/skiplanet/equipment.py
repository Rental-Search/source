# -*- coding: utf-8 -*-
from httplib2 import Http
from lxml import objectify

from .. import BaseSource, Product


def parse_equipment(args):
    root, tarif = args
    shop = root.xpath('//Magasin[@id=%s]' % tarif.ShopID.pyval)[0]
    station = root.xpath('//Station[@id=%s]' % shop.StationID.pyval)[0]
    pays = root.xpath('//Pays[@id=%s]' % station.PaysID.pyval)[0]
    pack = root.xpath('//Pack[@id=%s]' % tarif.PackID.pyval)[0]
    product = root.xpath('//Categorie[@id=%s]' % pack.CategorieID.pyval)[0]
    lat, lon = BaseSource().get_coordinates("%s %s %s" % (shop.Ville.pyval, shop.CP.pyval, pays.NomPays.pyval))
    summary = "%s - %s" % (product.NomCategorie.pyval, station.NomStation.pyval.capitalize())
    description = product.NomCategorie.pyval
    return Product({
        'id': '%s.%s' % (SourceClass().get_prefix(), tarif.get('id')),
        'summary': summary,
        'description': description,
        'categories': ['loisirs', 'sport', 'ski'],
        'lat': lat, 'lng': lon,
        'city': shop.Ville.pyval.capitalize(), 'zipcode': shop.CP.pyval,
        'price': tarif.d1.pyval,
        'owner': 'skiplanet',
        'owner_url': 'http://www.ski-planet.com/',
        'url': 'http://www.ski-planet.com/skiset/location-materiel-ski.php?partner=e-loue&ResortID=%s&ShopId=%s' % (
            station.get('id'), shop.get('id')
        ),
        'django_id': 'skiplanet.%s' % tarif.get('id'),
    })


class SourceClass(BaseSource):
    def get_prefix(self):
        return 'sources.skiplanet.equipment'
    
    def get_equipment(self, pool):
        response, content = Http().request("http://www.ski-planet.com/affiliation/flux-materiel.xml")
        root = objectify.fromstring(content)
        tarifs = [(root, el) for el in root.xpath('//Tarif')]
        return pool.map(parse_equipment, tarifs, len(tarifs) // BaseSource.processes)
    
    def get_docs(self):
        pool = self.get_pool()
        docs = self.get_equipment(pool)
        pool.close()
        pool.join()
        return docs
    
