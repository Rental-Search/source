# -*- coding: utf-8 -*-
from django.conf import settings

from haystack.query import SearchQuerySet

from products.models import Product, CarProduct, RealEstateProduct, Alert
from eloue.legacy import CompatSearchQuerySet

__all__ = ['product_search', 'product_only_search', 'car_search', 'realestate_search', 'alert_search']


product_search = SearchQuerySet().models(Product).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)._clone(klass=CompatSearchQuerySet)
product_only_search = SearchQuerySet().models(Product).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID).narrow('special:False')._clone(klass=CompatSearchQuerySet)
car_search = SearchQuerySet().models(CarProduct).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)._clone(klass=CompatSearchQuerySet)
realestate_search = SearchQuerySet().models(RealEstateProduct).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)._clone(klass=CompatSearchQuerySet)
alert_search = SearchQuerySet().models(Alert)._clone(klass=CompatSearchQuerySet)
