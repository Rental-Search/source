from products.models import Category, Product, Product2Category
import pytest
from products.templatetags.category import arrange_categories


@pytest.mark.usefixtures('categories_with_products')
def test_arrange_categories_returns_no_empty_categories():
    
    empty = Category.objects.get(name="vegetables")
    assert not Product2Category.objects.filter(category=empty).count()
    
    not_empty = Category.objects.get(name="fruit")
    assert Product2Category.objects.filter(category=not_empty).count()
    
    categories_map = {1:[2,3]}
    root_id = 1
    
    categories = arrange_categories(categories_map, root_id)
    assert empty not in categories
    assert not_empty in categories
    
    
    
    