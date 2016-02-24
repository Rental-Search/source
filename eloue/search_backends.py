from haystack_algolia.algolia_backend import AlgoliaSearchBackend
from haystack.backends import BaseEngine, BaseSearchQuery, log_query, SQ
from __builtin__ import NotImplementedError
from haystack.models import SearchResult
import re
from products.models import Product
from algoliasearch.client import Client
from django.core.exceptions import ImproperlyConfigured
from django.utils.datetime_safe import datetime
from haystack.inputs import AutoQuery
from haystack.constants import DEFAULT_ALIAS
from eloue.settings import ALGOLIA_INDICES


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
    
    
    @log_query
    def search(self, query_string, **kwargs):
        
        if re.match("\(.*\)", query_string):
            query_string = query_string[1:-1]
        
        result_class = kwargs.get('result_class') or SearchResult
        
        models = kwargs.get('models')
    
        # TODO query multiple models and choose index
        
        models = list(models)
        
        if models is None or len(models) > 1:
            models = [Product, ]
        
        distance_point = kwargs.get('distance_point')
        # TODO get distances
            
        start_offset = kwargs.get('start_offset', 0)
        end_offset = kwargs.get('end_offset', DEFAULT_PAGE_SIZE)
        per_page = end_offset - start_offset
        page = int(start_offset / per_page) if per_page>0 else 0
        
        orderby = kwargs.get('sort_by', [])
        
        if len(orderby) >=1:
            if len(orderby) == 1:
                orderby = ORDERINGS_MAP.get(orderby[0])\
                    if orderby[0] in ORDERINGS_MAP else orderby[0]
            elif len(orderby) > 1:
                orderby = ORDERINGS_MAP.get(','.join(orderby))
                
            master_settings = ALGOLIA_INDICES[model_label(models[0])]
        
            if 'slaves' in master_settings and orderby not in master_settings['slaves']:
                raise NotImplementedError("Unsupported ordering %s" % orderby)
        
        index = self._get_index_for(list(models)[0], orderby=orderby)
        
        params = dict(hitsPerPage=per_page, page=page)
        
        if query_string and query_string!='*':
            params["filters"]=query_string
            
        dwithin = kwargs.get('dwithin')
        # TODO use "field"?
        if dwithin:
            params['aroundLatLng'] = POINT % dwithin['point'].get_coords()
            params['aroundRadius'] = int(dwithin['distance'].m)
            
        search_terms = kwargs.get('search_terms')
            
        raw_results = index.search(search_terms, params)

        results = self._process_results(raw_results, result_class=result_class)

        return {
            'results': results["results"],
            'hits': results["hits"],
        }


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
    
        for i,(k,v) in enumerate(query_filter.children):
            
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
            v = int(v)
        except ValueError:
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
            
        if type(val) is int:
            kv = EQ_NUMERIC
        elif type(val) is bool:
            kv = EQ_FACET
            prepare = lambda x:str(x).lower()
        elif type(val) in (str, unicode): #TODO handle unicode and str correctly
            kv = EQ_FACET_STR
        elif isinstance(val, datetime):
            # TODO inclusive/exclusive range?
            kv = CMP[filter_type]
            prepare = lambda x:(x.created_at-datetime(1970,1,1)).total_seconds()
            # TODO better AutoQuery handling
        elif isinstance(value, AutoQuery):
            self.search_terms = str(value)
            return ""
        else:
            raise NotImplementedError("Unsupported value type: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(val)) )
        
        if filter_type in (['contains', 'exact',] + CMP.keys()):
            return kv % (field, prepare(value))
        elif filter_type == 'in':
            kvps = map(lambda x:kv % (field, prepare(x)), value)
            res = OR.join(kvps)
            if len(kvps) > 1:
                res = '('+res+')'
            return res
        else:
            raise NotImplementedError("Unsupported lookup: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(value)) ) 


    def build_params(self, spelling_query=None):
        kwargs = BaseSearchQuery.build_params(self, spelling_query=spelling_query)
        kwargs['search_terms'] = self.search_terms
        return kwargs
        
            
class EloueAlgoliaEngine(BaseEngine):
    """
    Provides a minimum of functionality to
    support existing usages:
        auto_query
        narrow
        filter(facet, numeric)
        dwithin
        order_by
    TODO:
        facet
        highlight
        distance
        more_like_this
        facet_counts
    """
    
    backend = EloueAlgoliaSearchBackend
    query = EloueAlgoliaSearchQuery
