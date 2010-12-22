# -*- coding: utf-8 -*-
from datetime import datetime
from pysolr import Solr
from multiprocessing import Pool, cpu_count

from django.conf import settings
from django.utils import importlib

from eloue.geocoder import GoogleGeocoder

SOURCES = getattr(settings, 'AFFILIATION_SOURCES', ['skiplanet', 'lv'])
BATCHSIZE = getattr(settings, 'AFFILIATION_BATCHSIZE', 1000)


class Product(dict):
    def __init__(self, *args, **kwargs):  # TODO: Need improvement
        super(Product, self).__init__(*args, **kwargs)
        self.update({ 
            'created_at': datetime.now(),
            'django_ct': 'products.product',
            'text': "%s %s" % (self['summary'], self['description']),
            'categories_exact': self['categories'],
            'owner_exact': self['owner'],
            'price_exact': self['price'],
        })
    

class BaseSource(object):
    processes = 2 * cpu_count()
    
    def get_pool(self):
        return Pool(processes=BaseSource.processes)
    
    def get_prefix(self):
        raise NotImplementedError
    
    def get_docs(self):
        raise NotImplementedError
    
    def get_coordinates(self, location):
        name, (lat, lon), radius = GoogleGeocoder().geocode(location)
        return lat, lon
    

class SourceManager(object):
    solr = Solr(settings.HAYSTACK_SOLR_URL, timeout=900)
    
    def __init__(self):
        self.sources = []
        for source in SOURCES:
            mod = importlib.import_module('eloue.products.sources.%s' % source)
            self.sources.append(getattr(mod, 'SourceClass')())
    
    def get_docs(self):
        docs = []
        for source in self.sources:
            docs.extend(source.get_docs())
        return docs
    
    def index_docs(self):
        docs = self.get_docs()
        total = len(docs)
        for start in range(0, total, BATCHSIZE):
            end = min(start + BATCHSIZE, total)
            self.__class__.solr.add(docs[start:end])
            self.__class__.solr.commit()
    
    def remove_docs(self):
        for source in self.sources:
            self.__class__.solr.delete(q="id:%s.*" % source.get_prefix())
            self.__class__.solr.commit()
    

if __name__ == '__main__':
    manager = SourceManager()
    manager.remove_docs()
    manager.index_docs()
