# -*- coding: utf-8 -*-
from haystack import site
from haystack.exceptions import AlreadyRegistered
from eloue.products.models import Product
from eloue.products.search_indexes import ProductIndex

site.register(Product, ProductIndex)
