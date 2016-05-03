from django.utils.six import with_metaclass
from products.search_indexes import DynamicFieldsDeclarativeMetaClass,\
    ProductIndex
from haystack import indexes
from haystack.fields import CharField, IntegerField
import pytest



def test_declarative_metaclass_fields_is_overriden():
    
    class TestIndex(with_metaclass(DynamicFieldsDeclarativeMetaClass, 
                                  indexes.Indexable, indexes.SearchIndex)):
        static_field = CharField(document=True)
    
    ti = TestIndex()
    assert isinstance(type(ti).fields, dict)
    
    
    class DynamicTestIndex(with_metaclass(DynamicFieldsDeclarativeMetaClass, 
                                  indexes.Indexable, indexes.SearchIndex)):
        static_field = CharField(document=True)

        _get_dynamic_fields = lambda self: self._fields
        
        def _set_dynamic_fields(self, x): 
            self._fields=x

    ti = DynamicTestIndex()
    assert isinstance(type(ti).fields, property)
    


def test_declarative_metaclass_mock_fields_added():
     
    class DynamicTestIndex(with_metaclass(DynamicFieldsDeclarativeMetaClass, 
                                  indexes.Indexable, indexes.SearchIndex)):
        static_field = CharField(document=True)
     
        def _get_dynamic_fields(self): 
            fs = self._fields.copy()
            fs.update({'dynamic_field':IntegerField()})
            return fs
         
        def _set_dynamic_fields(self, x):
            self._fields=x
        
    ti = DynamicTestIndex()
    assert 'dynamic_field' in ti.fields
    assert isinstance(ti.fields['dynamic_field'], IntegerField)
    
    

@pytest.fixture
def patch__get_absolute_url(monkeypatch):
    from products.models import Product, Category
    from products.models import Patron
    stub = lambda self, *args, **kwargs:'example'
    monkeypatch.setattr(Product, 'get_absolute_url', stub)
    monkeypatch.setattr(Category, 'get_absolute_url', stub)
    monkeypatch.setattr(Patron, 'get_absolute_url', stub)
    

    
@pytest.mark.usefixtures('product_with_properties', 'patch__get_absolute_url')
def test_product_index_with_declarative_metaclass(monkeypatch, product_with_properties):
    
    pi = ProductIndex()
    assert isinstance(type(pi).fields, property)
    assert hasattr(pi, '_set_dynamic_fields') and hasattr(pi, '_get_dynamic_fields')

#     import pdb ; pdb.set_trace()

    data = pi.full_prepare(product_with_properties)
    assert 'size' in pi.fields and 'color' in pi.fields
    assert isinstance(pi.fields['size'], IntegerField) 
    assert isinstance(pi.fields['color'], CharField)
    assert pi.fields['size'].faceted
    assert not pi.fields['color'].faceted
    assert 'size' in data and 'color' in data \
        and 'default_value' in data \
        and 'no_value' not in data
    
    assert data['size'] == 20 \
        and data['color'] == 'red' \
        and data['default_value'] == 5
#         and data['no_value'] == None
    
#     import pprint ; pprint.pprint(data)
    
    
    



