# -*- coding: utf-8 -*-
from decimal import Decimal as D
from httplib2 import Http
from lxml import objectify

from .. import BaseSource, Product


def parse_flat(args):
    station, residence = args
    thumbnails = residence.xpath("//Photo[@type='logement']")
    if thumbnails:
        thumbnail = thumbnails[0].pyval
    else:
        thumbnail = None
    if hasattr(residence, 'GeoLocalisation'):
        lat, lon = residence.GeoLocalisation.Latitude.pyval, residence.GeoLocalisation.Longitude.pyval
    else:
        lat, lon = BaseSource().get_coordinates("%s %s" % (residence.Ville.pyval, residence.CP.pyval))
    price = residence.xpath("//Tarif/PrixTTC[not(. < ../../Tarif/PrixTTC)]")[0].pyval
    return Product({
        'id': '%s.%s' % (SourceClass().get_prefix(), residence.get('id')),
        'summary': residence.NomResidence.pyval,
        'description': residence.DescriptionResidence_fr.pyval,
        'categories': ['lieu'],
        'lat': lat, 'lng': lon,
        'city': residence.Ville.pyval, 'zipcode': residence.CP.pyval,
        'price': D(str(price)) / D('7'),
        'owner': 'skiplanet',
        'owner_url': 'http://www.ski-planet.com/',
        'url': 'http://www.ski-planet.com/reservation/bonplan.php?partner=e-loue&StationID=%s' % station.get('id'),
        'thumbnail': thumbnail,
        'django_id': 'skiplanet.%s' % residence.get('id')
    })


class SourceClass(BaseSource):
    def get_prefix(self):
        return 'sources.skiplanet.flat'
    
    def get_flat(self, pool):
        response, content = Http().request("http://www.ski-planet.com/affiliation/flux.xml")
        root = objectify.fromstring(content)
        residences = []
        for station in root.xpath('//Station'):
            residences.extend([(station, residence) for residence in station.xpath('//Residence')])
        return pool.map(parse_flat, residences, len(residences) // BaseSource.processes)
    
    def get_docs(self):
        pool = self.get_pool()
        docs = self.get_flat(pool)
        pool.close()
        pool.join()
        return docs
    
