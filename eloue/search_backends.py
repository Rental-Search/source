from haystack_algolia.algolia_backend import AlgoliaSearchBackend
from haystack.backends import BaseEngine, BaseSearchQuery, log_query, SQ
from __builtin__ import NotImplementedError
from haystack.models import SearchResult
import re
from algoliasearch.client import Client
from django.core.exceptions import ImproperlyConfigured
import datetime
from haystack.inputs import AutoQuery
from haystack.constants import DEFAULT_ALIAS
from django.conf import settings
from decimal import Decimal, InvalidOperation

import haystack_algolia
haystack_algolia.algolia_backend.UPDATE_CHUNK_SIZE = 1000 # FIXME do not monkeypatch

EQ_NUMERIC = '%s=%s'
CMP = {'lt':'%s<%s',
       'lte': '%s<=%s', 
       'gt':'%s>%s', 
       'gte':'%s>=%s'}
EQ_FACET_STR = '%s:"%s"'
EQ_FACET = '%s:%s'
OR = ' OR '
AND = ' AND '
TAG_JOIN = ','
POINT = '%s,%s'
DEFAULT_PAGE_SIZE = 12

# Maps dynamic SearchQuerySet orderings to
# static algolia orderings 
ORDERINGS_MAP = {
    '-created_at_date,distance':'-created_at',
    '-created_at_date':'-created_at',
}

def model_label(model):
    return "{}.{}".format(model._meta.app_label, model._meta.model_name)

def is_algolia():
    return settings.HAYSTACK_CONNECTIONS['default']['ENGINE'] == 'eloue.search_backends.EloueAlgoliaEngine'


class IndexDoesNotExistException(Exception):
    pass


class EloueAlgoliaSearchBackend(AlgoliaSearchBackend):

    def __init__(self, connection_alias, **connection_options):
        super(AlgoliaSearchBackend, self).__init__(connection_alias, **connection_options)
        
        required_params = {"APP_ID", "API_KEY", "INDEX_NAME_PREFIX"}
        
        required_params.difference_update(connection_options.keys())
        
        if required_params:
            raise ImproperlyConfigured(
                'Parameters {} are missing for connection {}'\
                    .format(", ".join(required_params), connection_alias)) 

        self.connection_options = connection_options

        self.conn = Client(
            connection_options["APP_ID"], connection_options["API_KEY"])

        self.index_name_prefix = connection_options.get("INDEX_NAME_PREFIX", "") or ""

        self.setup_complete = True
        
    
    def _get_index_for(self, model, orderby=''):
        index_name = "{}{}".format(self.index_name_prefix, model_label(model))
        if orderby:
            index_name = index_name + '_' + orderby
        return self.conn.initIndex(index_name)
    

    def client_args(self, query_string, **kwargs):
        
        if re.match("\(.*\)", query_string):
            query_string = query_string[1:-1]
        
        models = kwargs.get('models', [])
    
        # TODO query multiple models and choose index
        
        models = list(models)
        
        if not models or len(models) > 1:
            raise NotImplementedError("Querying multiple models is not supported")
        
        label = model_label(models[0])
            
        if label not in settings.ALGOLIA_INDICES:
            raise IndexDoesNotExistException("Model %s is not configured" % label)
        
        distance_point = kwargs.get('distance_point')
        # TODO get distances
            
        start_offset = kwargs.get('start_offset', 0)
        end_offset = kwargs.get('end_offset', DEFAULT_PAGE_SIZE)
        per_page = end_offset - start_offset
        page = int(start_offset / per_page) if per_page>0 else 0
        
        orderby = kwargs.get('sort_by', [])
        
        if orderby:
            if len(orderby) == 1:
                orderby = ORDERINGS_MAP.get(orderby[0])\
                    if orderby[0] in ORDERINGS_MAP else orderby[0]
            elif len(orderby) > 1:
                orderby = ORDERINGS_MAP.get(','.join(orderby))
            
            master_settings = settings.ALGOLIA_INDICES[label]
                
            if 'slaves' in master_settings and orderby not in master_settings['slaves']:
                raise IndexDoesNotExistException('Ordering %s is not configured for model %s' % (orderby, label))
        
        index = self._get_index_for(list(models)[0], orderby=orderby)
        
        facets = kwargs.get('facets', {}).keys()
        
        params = dict(hitsPerPage=per_page, page=page, facets=facets)
        
        if query_string and query_string!='*':
            params["filters"]=query_string
            
        dwithin = kwargs.get('dwithin')
        # TODO use "field"?
        if dwithin:
            params['aroundLatLng'] = POINT % dwithin['point'].get_coords()
            params['aroundRadius'] = int(dwithin['distance'].m)
            
        search_terms = kwargs.get('search_terms')
        
        return index, search_terms, params
    
    @log_query
    def search(self, query_string, **kwargs):
        
        index, search_terms, params = self.client_args(query_string, **kwargs)
        
        raw_results = index.search(search_terms, params)
        
        result_class = kwargs.pop('result_class', SearchResult)
        
        results = self._process_results(raw_results, result_class=result_class, **kwargs)

        return {
            'results': results["results"],
            'hits': results["hits"],
            'facets': results["facets"],
        }

    
    def _process_results(self, raw_results, result_class, **kwargs):
        results = super(EloueAlgoliaSearchBackend, self)._process_results(raw_results, result_class)
        
        fields = {}
        
        if "facets" in raw_results and "facets_stats" in raw_results:
            for facet in raw_results["facets"]:
                try: #FIXME type is guessed
                    fields[facet] = [(Decimal(k),v) 
                                     for k,v in raw_results["facets"][facet].items()]
                except InvalidOperation:
                    fields[facet] = [(k,v) 
                                     for k,v in raw_results["facets"][facet].items()]
        
        results['facets'] = {
                             'dates':{},
                             'fields':fields,
                             'queries':{},
                             }
        
        return results
        
    
class EloueAlgoliaSearchQuery(BaseSearchQuery):
    
    def __init__(self, using=DEFAULT_ALIAS):
        BaseSearchQuery.__init__(self, using=using)
        self.search_terms = ""
        
    def _clone(self, klass=None, using=None):
        clone = super(EloueAlgoliaSearchQuery, self)._clone(klass=klass, using=using)
        clone.search_terms = self.search_terms
        return clone
        
    # This removes "content" lookups from the query
    # so they do not take part in the unified filter ("filters")
    # generation, and stores them to use for algolia's 
    # full text search query ("query")
    def add_filter(self, query_filter, use_or=False):
    
        for i, child in enumerate(query_filter.children):
            
            if isinstance(child, SQ): 
                continue
            
            k, v = child
            
            if k == 'content':
                self.search_terms = str(v)
                del query_filter.children[i]
                break
        
        if not(query_filter.children):
            return
                
        super(EloueAlgoliaSearchQuery, self).add_filter(query_filter, use_or=use_or)
    
    
    #TODO: facet, models
    def add_narrow_query(self, query):
        # TODO real implementation of narrow instead of delegating to filter?
        k, v = query.split(':')
        try:
            v = Decimal(v)
        except InvalidOperation:
            pass
        self.add_filter(SQ(**{k:v}))
    
    
    def build_query_fragment(self, field, filter_type, value):
        
        prepare = lambda x:x
        
        val = value
        
        if type(val) is list:
            if len(value) == 0:
                return ""
            vtypes = set(type(x) for x in val)
            if len(vtypes) > 1:
                raise NotImplementedError("Multiple types not supported in iterable: %s" % (vtypes,))
            val = value[0]
        
        if filter_type in ['contains', 'exact','in',]:
            
            if type(val) in [int, Decimal]:
                kv = EQ_NUMERIC
            elif type(val) is bool:
                kv = EQ_FACET
                prepare = lambda x:str(x).lower()
            elif type(val) in (str, unicode): #TODO handle unicode and str correctly
                kv = EQ_FACET_STR
            # TODO better AutoQuery handling
            elif isinstance(value, AutoQuery):
                self.search_terms = str(value)
                return ""
            else:
                raise NotImplementedError("Unsupported lookup: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(value)) ) 

            
            if filter_type in ['contains', 'exact']:
                return kv % (field, prepare(value))
            elif filter_type == 'in':
                kvps = map(lambda x:kv % (field, prepare(x)), value)
                res = OR.join(kvps)
                if len(kvps) > 1:
                    res = '('+res+')'
                return res
        
        elif filter_type in CMP.keys():
            kv = CMP[filter_type]
            if isinstance(val, datetime.datetime):
                # TODO inclusive/exclusive range?
                prepare = lambda x:(x-datetime.datetime.fromtimestamp(0)).total_seconds()

            elif type(val) in [int, float, Decimal]:
                pass
            else:
                raise NotImplementedError("Unsupported lookup: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(value)) ) 

            return kv % (field, prepare(value))
            
        else:
            raise NotImplementedError("Unsupported lookup: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(value)) ) 


    def build_params(self, spelling_query=None):
        kwargs = BaseSearchQuery.build_params(self, spelling_query=spelling_query)
        kwargs['search_terms'] = self.search_terms
        return kwargs
        

#TODO remove dependencies on other eloue apps 
#TODO separate into an app
class EloueAlgoliaEngine(BaseEngine):
    """
    Provides a minimum of functionality to
    support existing usages:
        auto_query
        narrow
        filter(facet, numeric)
        dwithin
        order_by
        facet
        facet_counts
    TODO:
        highlight
        distance
        more_like_this
    """
    
    backend = EloueAlgoliaSearchBackend
    query = EloueAlgoliaSearchQuery
