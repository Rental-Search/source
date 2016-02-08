from haystack_algolia.algolia_backend import AlgoliaSearchBackend
from haystack.backends import BaseEngine, BaseSearchQuery, log_query
from __builtin__ import NotImplementedError
from haystack.models import SearchResult
import re
from products.models import Product


EQ_NUMERIC = '%s=%s'
EQ_FACET = '%s:"%s"'
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

    def build_query_fragment(self, field, filter_type, value):
        
        if type(value) is list:
            if len(value) == 0:
                return ""
            # Assuming all elements are of same type
            val = value[0]
        elif type(value) in (str, int, bool):
            val = value
        else:
            raise NotImplementedError("Unsupported value type: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(value)) )
        
        kv = EQ_NUMERIC if type(val) is int else EQ_FACET
        
        import pdb ; pdb.set_trace()
        
        if filter_type in ('contains', 'exact'):
            return kv % (field, value)
        elif filter_type == 'in':
            kvps = map(lambda x:kv % (field, x), value)
            res = ('('+OR.join(kvps)+')') if len(kvps) > 1 else OR.join(kvps)
            return res
        else:
            raise NotImplementedError("Unsupported lookup: field=%s, filter_type=%s, value=%s" 
                                      % (field, filter_type, type(value)) ) 


class EloueAlgoliaEngine(BaseEngine):

    backend = EloueAlgoliaSearchBackend
    query = EloueAlgoliaSearchQuery
