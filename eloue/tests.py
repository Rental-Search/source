import pytest
from collections import namedtuple
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from decimal import Decimal
from __builtin__ import NotImplementedError
from products.models import Product
from accounts.models import Patron, Address
from eloue.search_backends import IndexDoesNotExistException
import datetime

SearchParams = namedtuple('SearchParams', ['index', 'query', 'params'])

search_params = SearchParams._make((None,None,None,))

def search(self, query_string, **kwargs):
    global search_params    
    search_params = SearchParams._make(self.client_args(query_string, **kwargs))
    return {
        'results': [],
        'hits': 0,
    }


@pytest.fixture(autouse=True)
def prepare(monkeypatch, settings):
    settings.HAYSTACK_CONNECTIONS['default'] = settings.HAYSTACK_CONNECTIONS['algolia']
    monkeypatch.setattr('eloue.search_backends.EloueAlgoliaSearchBackend.search', search)


@pytest.fixture()
def all_models_search_queryset(monkeypatch):
    from haystack.query import SearchQuerySet
    sqs = SearchQuerySet()
    return sqs


@pytest.fixture()
def global_product_search(all_models_search_queryset):
    return all_models_search_queryset.models(Product)


@pytest.fixture()
def global_patron_search(all_models_search_queryset):
    return all_models_search_queryset.models(Patron)


@pytest.fixture()
def search_queryset(all_models_search_queryset):
    return all_models_search_queryset.models(Product)


@pytest.fixture()
def product_search():
    from products.search import product_search
    return product_search
    

@pytest.fixture()
def patron_search():
    from accounts.search import patron_search
    return patron_search


class TestEloueAlgoliaEngine(object):
    """
    Test SearchQuerySet functionality used in eloue the apps
    """

    def test_auto_query(self, search_queryset):
        sqs = search_queryset
        
        list(sqs.auto_query('remorque'))
        
        assert search_params.query == 'remorque'
    
    
    def test_narrow(self, search_queryset):
        sqs = search_queryset
        
        list(sqs.narrow('a:b'))
        
        assert search_params.params['filters'] == 'a:"b"'
        
        list(sqs.narrow('a:3'))
        assert search_params.params['filters'] == 'a=3'
        
        list(sqs.narrow('a:1.3'))
        assert search_params.params['filters'] == 'a=1.3'
        
        list(sqs.narrow('a:b').narrow('c:3'))
        assert search_params.params['filters'] == 'a:"b" AND c=3'
    
    
    def test_dwitihin(self, search_queryset):
        sqs = search_queryset
        
        latlong = (0.4,5.1)
        list(sqs.dwithin('location', Point(latlong), Distance(km=10)))
        assert search_params.params['aroundLatLng'] == "0.4,5.1"
        assert search_params.params['aroundRadius'] == 10000
       
        
    def test_filter(self, search_queryset):
        sqs = search_queryset
        
        
        # empty filter
        list(sqs.filter())
        assert 'filters' not in search_params.params
        
        
        # str equals, contains
        list(sqs.filter(a="a"))
        assert search_params.params['filters'] == 'a:"a"'
        
        list(sqs.filter(a__exact="a"))
        assert search_params.params['filters'] == 'a:"a"'
        
        list(sqs.filter(a__contains="a"))
        assert search_params.params['filters'] == 'a:"a"'
        
        
        # numeric equality
        list(sqs.filter(a=3))
        assert search_params.params['filters'] == "a=3"
        
        with pytest.raises(NotImplementedError):
            list(sqs.filter(a=3.14))

        list(sqs.filter(a=Decimal('3.14')))
        assert search_params.params['filters'] == "a=3.14"
        
        
        # numeric lt, gt, lte, gte
        list(sqs.filter(a__gte=2))
        assert search_params.params['filters'] == "a>=2"
        
        list(sqs.filter(a__lte=2))
        assert search_params.params['filters'] == "a<=2"
        
        list(sqs.filter(a__gt=2))
        assert search_params.params['filters'] == "a>2"
        
        list(sqs.filter(a__lt=2))
        assert search_params.params['filters'] == "a<2"
        
        list(sqs.filter(a__gte=2.1))
        assert search_params.params['filters'].startswith("a>=2.1")
        
        list(sqs.filter(a__lte=2.1))
        assert search_params.params['filters'].startswith("a<=2.1")
        
        list(sqs.filter(a__gt=2.1))
        assert search_params.params['filters'].startswith("a>2.1")
        
        list(sqs.filter(a__lt=2.1))
        assert search_params.params['filters'].startswith("a<2.1")
        
        list(sqs.filter(a__gte=Decimal('2.1')))
        assert search_params.params['filters'] == "a>=2.1"
        
        list(sqs.filter(a__lte=Decimal('2.1')))
        assert search_params.params['filters'] == "a<=2.1"
        
        list(sqs.filter(a__gt=Decimal('2.1')))
        assert search_params.params['filters'] == "a>2.1"
        
        list(sqs.filter(a__lt=Decimal('2.1')))
        assert search_params.params['filters'] == "a<2.1"
        
        
        # datetime lt, gt, lte, gte
        list(sqs.filter(a__lt=datetime.datetime(1970,1,1,1,0,0,0)))
        assert search_params.params['filters'] == "a<0.0"
        
        list(sqs.filter(a__gt=datetime.datetime(2016,1,1,1,0,0,0)))
        assert search_params.params['filters'] == "a>1451606400.0"
        
        list(sqs.filter(a__lte=datetime.datetime(1970,1,1,1,0,0,0)))
        assert search_params.params['filters'] == "a<=0.0"
        
        list(sqs.filter(a__gte=datetime.datetime(2016,1,1,1,0,0,0)))
        assert search_params.params['filters'] == "a>=1451606400.0"
        
        #TODO add ohter datetime filters
        
        
        # in
        list(sqs.filter(a__in=["a", "b", "c"]))
        assert search_params.params['filters'] == 'a:"a" OR a:"b" OR a:"c"'
        
        list(sqs.filter(a__in=[1, 2, 3]))
        assert search_params.params['filters'] == 'a=1 OR a=2 OR a=3'
        
        with pytest.raises(NotImplementedError):
            list(sqs.filter(a__in=[1.2, 2.3, 3.4]))
        
        list(sqs.filter(a__in=[Decimal('1.2'), Decimal('2.3'), Decimal('3.4')]))
        assert search_params.params['filters'] == 'a=1.2 OR a=2.3 OR a=3.4'
        
        
        # negation
        list(sqs.exclude(a__gte=datetime.datetime(1970,1,1,1)))
        assert search_params.params['filters'] == "NOT (a>=0.0)"
        
        
        # mixed filters
        list(sqs.filter(a__gt=1, a__lte=10))
        assert search_params.params['filters'] == 'a<=10 AND a>1'
        
        list(sqs.filter(a__gt=1, a__lte=10).filter(b__contains='milk'))
        assert search_params.params['filters'] == 'a<=10 AND a>1 AND b:"milk"'
        
        list(sqs.filter(a__gt=1, a__lte=10).filter(b__contains='milk').filter(c__in=['pastry', 'dairy']))
        assert search_params.params['filters'] == \
            'a<=10 AND a>1 AND b:"milk" AND (c:"pastry" OR c:"dairy")'
        
        list(sqs.narrow("aa:bb").filter(a__gt=1, a__lte=10).filter(b__contains='milk')
             .filter(c__in=['pastry', 'dairy']).exclude(d=200))
        assert search_params.params['filters'] == \
            'aa:"bb" AND a<=10 AND a>1 AND b:"milk" AND (c:"pastry" OR c:"dairy") AND NOT (d=200)'
        
    
    def test_facet(self, search_queryset):
        sqs = search_queryset
        
        list(sqs.facet('a'))
        assert search_params.params['facets'] == ['a',]
        
        list(sqs.facet('a').facet('b').facet('c'))
        assert set(search_params.params['facets']) == set(['a','b','c'])
        
    
    def test_models(self, all_models_search_queryset, global_patron_search, global_product_search, settings):
        
        prefix = settings.HAYSTACK_CONNECTIONS['algolia']['INDEX_NAME_PREFIX']
        product_label = Product._meta.app_label + '.' +  Product._meta.model_name
        patron_label = Patron._meta.app_label + '.' +  Patron._meta.model_name
        
        with pytest.raises(IndexDoesNotExistException):
            list(all_models_search_queryset.models(Address))
        
        with pytest.raises(NotImplementedError):
            list(all_models_search_queryset)
    
        multiple_models_search_queryset = all_models_search_queryset.models(Patron, Product)
        with pytest.raises(NotImplementedError):
            list(multiple_models_search_queryset)
        
        list(global_patron_search)
        assert search_params.index.index_name == prefix + patron_label 
    
        list(global_product_search)
        assert search_params.index.index_name == prefix + product_label 
    
        
    def test_order_by(self, search_queryset, all_models_search_queryset, settings):
        sqs = search_queryset
        
        prefix = settings.HAYSTACK_CONNECTIONS['algolia']['INDEX_NAME_PREFIX']
        product_label = Product._meta.app_label + '.' +  Product._meta.model_name
        order_by_field = 'price'
        
        with pytest.raises(IndexDoesNotExistException):
            list(sqs.order_by('-nesslessness'))
        
        list(sqs.order_by('price'))
        assert search_params.index.index_name == prefix + product_label + '_' + order_by_field
        
        list(sqs.order_by('-price'))
        assert search_params.index.index_name == prefix + product_label + '_-' + order_by_field
        
    
    def test_more_like_this(self, search_queryset):
        sqs = search_queryset
        assert False


    def facet_counts(self, search_queryset):
        sqs = search_queryset
        assert False
            

    def test_eloue_queries(self, product_search, patron_search, settings):
        sqs = search_queryset
        
        prefix = settings.HAYSTACK_CONNECTIONS['algolia']['INDEX_NAME_PREFIX']
        
        # products search
        
        product_label = Product._meta.app_label + '.' +  Product._meta.model_name
        
        list(product_search)
        
        assert search_params.index.index_name == prefix + product_label
        assert search_params.params['filters'] == 'is_archived:false AND sites=%s' % (settings.SITE_ID, )
        assert set(search_params.params['facets']) == set(['sites_exact','categories_exact','owner_exact', 'price_exact', 'pro_owner_exact'])
        
        # patrons search
        
        patron_label = Patron._meta.app_label + '.' +  Patron._meta.model_name
        
        list(patron_search)
        
        assert search_params.index.index_name == prefix + patron_label
        assert search_params.params['filters'] == 'sites=%s' % (settings.SITE_ID, )
        assert set(search_params.params['facets']) == set(['sites_exact'])
        
        
    