# -*- coding: utf-8 -*-
import types

from django.conf import settings
from django.contrib.gis.db.models import GeoManager
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.db.models import Manager, Q
from django.db.models.fields import FieldDoesNotExist

from mptt.managers import TreeManager as OriginalTreeManager

from products.choices import UNIT, STATUS


class ProductManager(GeoManager):
    def active(self, *args, **kwargs):
        return self.filter(*args, is_allowed=True, **kwargs)
    
    def archived(self, *args, **kwargs):
        return self.filter(*args, is_archived=True, is_allowed=True, **kwargs)

class CurrentSiteProductManager(CurrentSiteManager, ProductManager):
    def get_queryset(self):
        qs = super(CurrentSiteProductManager, self).get_queryset()
        qs = qs.filter(product2category__site_id=settings.SITE_ID)
        return qs.distinct()

class CurrentSiteProduct2CategoryManager(CurrentSiteManager):
    def get_queryset(self):
        qs = super(CurrentSiteProduct2CategoryManager, self).get_queryset()
        return qs.distinct()

class PriceManager(Manager):
    def __init__(self):
        super(PriceManager, self).__init__()
        for unit in UNIT.enum_dict:
            setattr(self, unit.lower(), types.MethodType(self._filter_factory(unit), self))
    
    @staticmethod
    def _filter_factory(unit):
        def filter(self):
            return self.get_query_set().filter(unit=UNIT[unit])
        return filter
    

class QuestionManager(Manager):
    def __init__(self):
        super(QuestionManager, self).__init__()
        for status in STATUS.enum_dict:
            setattr(self, status.lower(), types.MethodType(self._filter_factory(status), self))
    
    @staticmethod
    def _filter_factory(status):
        def filter(self):
            return self.get_query_set().filter(status=STATUS[status])
        return filter
    

class TreeManager(OriginalTreeManager):
    def get_query_set(self):
        return super(TreeManager, self).get_query_set().filter(sites__id__exact=settings.SITE_ID).order_by(self.tree_id_attr, self.left_attr)
    
