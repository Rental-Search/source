# -*- coding: utf-8 -*-
from haystack import site
from haystack.exceptions import AlreadyRegistered
from eloue.products.models import Product
from eloue.products.search_indexes import ProductIndex

try:
    site.register(Product, ProductIndex)
except AlreadyRegistered:
    pass
