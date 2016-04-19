# -*- coding: utf-8 -*-
import pytest
from django.core.management import call_command
from _pytest.monkeypatch import monkeypatch


@pytest.fixture()
def product_with_properties(settings, transactional_db):
    from accounts.models import Patron
    from products.models import Product
    settings.SITE_ID = 1
    settings.DEFAULT_SITES = [1,]
    call_command('loaddata', 'product_with_properties.yaml')
    for p in Patron.objects.all(): 
        p.set_password(p.username)
        p.save()
    prod = Product.objects.get(pk=1)
    return prod

@pytest.fixture()
def api_client(monkeypatch):
    from rest_framework.test import APIClient

    def post_with_redirects(self, path, data=None, format=None, content_type=None, **extra):
        follow = extra.pop('follow', False)
        data, content_type = self._encode_data(data, format, content_type)
        response = self.generic('POST', path, data, content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response
     
    monkeypatch.setattr(APIClient, 'post', post_with_redirects)
     
    APIClient.post = post_with_redirects
    
    return APIClient()
