# -*- coding: utf-8 -*-
import types

from django.conf import settings
from django.contrib.gis.db.models import GeoManager
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.db.models import Manager, Q
from django.db.models.fields import FieldDoesNotExist

from mptt.managers import TreeManager as OriginalTreeManager


class ProductManager(GeoManager):
    def active(self):
        return self.filter(is_archived=False, is_allowed=True)
    
    def archived(self):
        return self.filter(is_archived=True, is_allowed=True)

class CurrentSiteProductManager(CurrentSiteManager, ProductManager):
    pass

class PriceManager(Manager):
    def __init__(self):
        from eloue.products.models import UNIT
        super(PriceManager, self).__init__()
        for unit in UNIT.enum_dict:
            setattr(self, unit.lower(), types.MethodType(self._filter_factory(unit), self))
    
    @staticmethod
    def _filter_factory(unit):
        from eloue.products.models import UNIT
        
        def filter(self):
            return self.get_query_set().filter(unit=UNIT[unit])
        return filter
    

class QuestionManager(Manager):
    def __init__(self):
        from eloue.products.models import STATUS
        super(QuestionManager, self).__init__()
        for status in STATUS.enum_dict:
            setattr(self, status.lower(), types.MethodType(self._filter_factory(status), self))
    
    @staticmethod
    def _filter_factory(status):
        from eloue.products.models import STATUS
        
        def filter(self):
            return self.get_query_set().filter(status=STATUS[status])
        return filter
    

class TreeManager(OriginalTreeManager):
    def get_query_set(self):
        return super(TreeManager, self).get_query_set().filter(sites__id__exact=settings.SITE_ID).order_by(self.tree_id_attr, self.left_attr)
    
