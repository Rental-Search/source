# -*- coding: utf-8 -*-
from products.serializers import ProductSerializer
import pytest
from rest_framework.fields import CharField, IntegerField
from django.core.urlresolvers import reverse
from pytest_django.fixtures import transactional_db
from products.tests.conftest import product_with_properties
from rest_framework.test import APIClient


def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)



# @pytest.mark.usefixtures('product_with_properties')
# def test_update_product_with_properties(product_with_properties, client, transactional_db):
#     client.login(username='johndoe', password='johndoe')
#     response = client.patch(_location('product-detail', pk=1), data={'size':38})
#     assert response.status_code == 200
#     assert response.data['id'] == 1
#     assert response.data['size'] == 38


@pytest.mark.usefixtures('product_with_properties')
def test_create_product_with_properties(transactional_db):
    
    client = APIClient()
    
    client.login(username='johndoe@example.com', password='johndoe')
    
    product = { 
        'summary': u'Orange', 
        'deposit_amount': 10.00, 
        'currency': u'EUR',
        'description': u'An orange', 
        'address': _location('address-detail', pk=1),
        'category': _location('category-detail', pk=1),
        'owner': _location('patron-detail', pk=1), 
        'color': u'orange',
        'size': 25}
    
    response = client.post(_location('product-list'), data=product, follow=True)
    
    assert response.status_code == 201
    
    data = response.data
    
    assert data['size'] == 20 \
        and data['color'] == 'red' \
        and data['default_value'] == 5
        


@pytest.mark.usefixtures('product_with_properties')
def test_serialize_properties(product_with_properties):
    
    ps = ProductSerializer(instance=product_with_properties)
    fs = ps.fields
     
    assert 'color' in fs and 'size' in fs
    assert isinstance(fs['color'], CharField) and isinstance(fs['size'], IntegerField)
    
    data = ps.data
    
    assert 'color' in data and 'size' in data
    assert data['size'] == 20 \
        and data['color'] == 'red' \
        and data['default_value'] == 5


@pytest.mark.usefixtures('product_with_properties')
def test_deserialize_properties(product_with_properties, transactional_db):
    
    from products.models import Product
    
    data = {'id': 1, 
            'summary': u'Orange', 
            'deposit_amount': 10.00, 
            'currency': u'EUR', 
            'description': u'', 
            'address': _location('address-detail', pk=1),
            'category': _location('category-detail', pk=1),
            'owner': _location('patron-detail', pk=1), 
            'color': u'orange',
            'size': 25}

    ps = ProductSerializer(data=data)
    
    assert not ps.errors
    
    ps.save()
    
    p = Product.objects.get(pk=ps.object.pk)
    
    assert p.properties.count() == 3
    assert p.properties.filter(property_type__attr_name='color', value_str='orange').exists()
    assert p.properties.filter(property_type__attr_name='size', value_str='25').exists()
    assert p.properties.filter(property_type__attr_name='default_value', value_str='5').exists()
    

# TODO check with invalid category

    
# 
# @pytest.mark.xfail
# def test_cant_deserialize_with_new_category_for_existing_object(product_with_properties):
#     assert 0
#     
# @pytest.mark.xfail
# def test_cant_add_fields_with_colliding_names(product_with_properties):
#     # Properties can't have the same names as product fields
#     assert 0
