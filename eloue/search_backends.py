from haystack_algolia.algolia_backend import AlgoliaSearchBackend
from haystack.backends import BaseEngine, BaseSearchQuery, log_query
from __builtin__ import NotImplementedError
from haystack.models import SearchResult
import re
from products.models import Product


EQ_NUMERIC = '%s=%s'
EQ_FACET = '%s:"%s"'
EQ_FACET_NOQ = '%s:%s'
OR = ' OR '
AND = ' AND '
TAG_JOIN = ','
DEFAULT_PAGE_SIZE = 12


class EloueAlgoliaSearchBackend(AlgoliaSearchBackend):
    
    def __init__(self, connection_alias, **connection_options):
        AlgoliaSearchBackend.__init__(self, connection_alias, **connection_options)
        self.setup_complete = True
    
    @log_query
    def search(self, query_string, **kwargs):
        
        if re.match("\(.*\)", query_string):
            query_string = query_string[1:-1]
        
        result_class = kwargs.get('result_class') or SearchResult

        models = kwargs.get('models')

        # TODO query multiple models and choose index
        if models is None or len(models) > 1:
            models = [Product, ]
            
        start_offset = kwargs.get('start_offset', 0)
        end_offset = kwargs.get('end_offset', DEFAULT_PAGE_SIZE)
        per_page = end_offset - start_offset
        page = int(start_offset / per_page) if per_page>0 else 0

        index = self._get_index_for(list(models)[0])
        
        params = dict(hitsPerPage=per_page, page=page,\
                      facets="*")
        
        if query_string and query_string!='*':
            params["filters"]=query_string
            
        raw_results = index.search("", params)

        results = self._process_results(raw_results, result_class=result_class)

        return {
            'results': results["results"],
            'hits': results["hits"],
        }

class EloueAlgoliaSearchQuery(BaseSearchQuery):
    
    #TODO: facet, narrow, models
    
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
            kv = EQ_FACET_NOQ
            prepare = lambda x:str(x).lower()
        elif type(val) in (str, unicode): #TODO handle unicode and str correctly
            kv = EQ_FACET
        else:
            raise NotImplementedError("Unsupported value type: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(val)) )
        
        if filter_type in ('contains', 'exact'):
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


class EloueAlgoliaEngine(BaseEngine):

    backend = EloueAlgoliaSearchBackend
    query = EloueAlgoliaSearchQuery
