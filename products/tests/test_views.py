from rest_framework.status import HTTP_200_OK
import pytest
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from urlparse import urlparse


class TestImportedObjectRedirectView(object):
    
    # tests both the view and rentalcomare.com import
    # TODO make test data/config more general
    
    # products
    @pytest.mark.usefixtures('imported_product')
    def test_redirect_to_imported_object_product(self, imported_product, client):
        p = imported_product
        
        url = reverse('product_detail_rentalcompare', kwargs={'original_id':p.original_id,
                                                        'original_slug':'test_slug'})
        
        resp = client.get(url, follow=True)
        
        assert hasattr(resp, "redirect_chain")
        assert urlparse(zip(*resp.redirect_chain)[0][-1]).path == p.get_absolute_url()
    
    
    @pytest.mark.usefixtures('imported_product')
    def test_redirect_to_fallback_url_product(self, imported_product, client):
        
        url = reverse('product_detail_rentalcompare', kwargs={'original_id':2,
                                                        'original_slug':'test_slug'})
        
        resp = client.get(url, follow=True)
    
        assert resp.status_code == HTTP_200_OK
        assert 'product_list' in resp.context


    # patrons
    @pytest.mark.usefixtures('imported_product')
    def test_redirect_to_imported_object_patron(self, imported_product, client):
        p = imported_product.owner
        
        url = reverse('patron_detail_rentalcompare', kwargs={'username':p.username})
        
        resp = client.get(url, follow=True)
        
        req = HttpRequest()
        req.META = resp.request
        
        assert hasattr(resp, "redirect_chain")
        assert urlparse(zip(*resp.redirect_chain)[0][-1]).path == p.get_absolute_url()
    
    
    @pytest.mark.usefixtures('imported_product')
    def test_redirect_to_fallback_url_patron(self, imported_product, client):
        
        url = reverse('patron_detail_rentalcompare', kwargs={'username':"janedoe"})
        
        resp = client.get(url, follow=True)
    
        assert resp.status_code == HTTP_200_OK
        assert 'product_list' in resp.context
