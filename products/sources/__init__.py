# -*- coding: utf-8 -*-
import hashlib
import hmac
import logbook

from datetime import datetime
from multiprocessing import Pool, cpu_count
from urlparse import urlparse, urljoin
from itertools import islice

from django.conf import settings
from django.utils import importlib

from haystack import connections as haystack_connections
from haystack.constants import DJANGO_CT, DJANGO_ID, ID, DEFAULT_ALIAS

from eloue.geocoder import GoogleGeocoder
from eloue.utils import generate_camo_url

log = logbook.Logger('eloue.rent.sources')

SOURCES = getattr(settings, 'AFFILIATION_SOURCES', ['skiplanet', 'lv'])
BATCHSIZE = getattr(settings, 'AFFILIATION_BATCHSIZE', 100)

CAMO_URL = getattr(settings, 'CAMO_URL', 'https://media.e-loue.com/proxy/')
CAMO_KEY = getattr(settings, 'CAMO_KEY')

def meta_class(app_label, module_name):
    class Meta(object):
        def _get_prefix(self):
            return '%s.%s' % (self.app_label, self.module_name)
    for k, v in zip(('app_label', 'module_name'), (app_label, module_name)):
        setattr(Meta, k, v)
    return Meta

class Product(object):
    def __init__(self, data_dict, pk=None, meta=None):  # TODO: Need improvement
        self.data_dict = data_dict
        self.data_dict.update({
            ID: '%s.%s' % (meta._get_prefix(), pk),
            DJANGO_ID: '%s.%s' % (meta.module_name, pk),
            DJANGO_CT: 'products.product',
            'created_at': datetime.now(),
            'text': "%s %s" % (self['summary'], self['description']),
            'categories_exact': self['categories'],
            'owner_exact': self['owner'],
            'price_exact': self['price'],
            'sites': settings.DEFAULT_SITES,
            'sites_exact': settings.DEFAULT_SITES,
            'thumbnail': generate_camo_url(self['thumbnail'].encode('utf-8')) if 'thumbnail' in self and self['thumbnail'] else None,
        })
        self._meta = meta
        self._pk = pk

    def _camo_url(self, url):
        parts = urlparse(url)
        parts = {
            'scheme': parts.scheme,
            'hostname': parts.hostname,
            'path': parts.path if not parts.path.startswith('//') else parts.path[1:],
            'params': parts.params
        }
        url = urljoin("%(scheme)s://%(hostname)s" % parts, "%(path)s?%(params)s" % parts)
        digest = hmac.new(CAMO_KEY, url, hashlib.sha1).hexdigest()
        return "%s%s?url=%s" % (CAMO_URL, digest, url)

    def _get_pk_val(self):
        return self._pk

class BaseSource(object):
    processes = 2 * cpu_count()

    def get_pool(self):
        return Pool(processes=BaseSource.processes)

    def get_prefix(self):
        _meta = getattr(self.__class__, '_meta', None)
        if _meta is not None:
            return '%s.%s' % (_meta._get_prefix())
        raise NotImplementedError

    def get_docs(self):
        raise NotImplementedError

    def get_coordinates(self, location):
        return GoogleGeocoder().geocode(location)[1]

    def make_product(self, *args, **kwargs):
        if 'meta' not in kwargs:
            kwargs['meta'] = self.__class__._meta
        return Product(*args, **kwargs)

    def full_prepare(self, obj):
        return obj.data_dict

class SourceManager(object):
    search_backend = None

    def __init__(self, sources=()):
        self.sources = [
            getattr(importlib.import_module('products.sources.%s' % source), 'SourceClass')()
            for source in (sources if len(sources) else SOURCES)
        ]

    def get_docs(self, source):
        for el in source.get_docs():
            yield el

    def get_backend(self):
        if not self.search_backend:
            self.search_backend = haystack_connections[DEFAULT_ALIAS].get_backend()
        return self.search_backend

    def index_docs(self, source):

        def next_docs(source):
            docs = self.get_docs(source)
            while True:
                l = list(islice(docs, BATCHSIZE)) # FIXME: doesn't this just start with BATCHSIZE offset?
                if l: yield l
                else: return

        search_backend = self.get_backend()
        for batch in next_docs(source):
            search_backend.update(source, batch)


    def remove_docs(self, source):
        self.get_backend().clear([source], commit=True)


if __name__ == '__main__':
    manager = SourceManager()
    manager.remove_docs()
    manager.index_docs()
