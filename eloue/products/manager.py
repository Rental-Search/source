# -*- coding: utf-8 -*-
import types

from django.conf import settings
from django.contrib.gis.db.models import GeoManager
from django.db import models
from django.db.models import Manager, Q
from django.db.models.fields import FieldDoesNotExist

from mptt.managers import TreeManager as OriginalTreeManager


class ProductManager(GeoManager):
    def active(self):
        return self.filter(is_archived=False, is_allowed=True)
    
    def archived(self):
        return self.filter(is_archived=True, is_allowed=True)
    
    def last_added(self):
        return self.order_by('-modified_at')
    
    def last_added_near(self, l):
        return self.filter(
            ~Q(address__position=None)
        ).distance(
            l, field_name='address__position'
        ).extra(
            select={'modified_date': 'date(modified_at)'}
        ).order_by('-modified_date', 'distance')


class CurrentSiteProductManager(ProductManager):
    def __init__(self, field_name=None):
        super(CurrentSiteProductManager, self).__init__()
        self.__field_name = field_name
        self.__is_validated = False
    
    def _validate_field_name(self):
        field_names = self.model._meta.get_all_field_names()
        
        # If a custom name is provided, make sure the field exists on the model
        if self.__field_name is not None and self.__field_name not in field_names:
            raise ValueError("%s couldn't find a field named %s in %s." % \
                (self.__class__.__name__, self.__field_name, self.model._meta.object_name))
        
        # Otherwise, see if there is a field called either 'site' or 'sites'
        else:
            for potential_name in ['site', 'sites']:
                if potential_name in field_names:
                    self.__field_name = potential_name
                    self.__is_validated = True
                    break
        
        # Now do a type check on the field (FK or M2M only)
        try:
            field = self.model._meta.get_field(self.__field_name)
            if not isinstance(field, (models.ForeignKey, models.ManyToManyField)):
                raise TypeError("%s must be a ForeignKey or ManyToManyField." % self.__field_name)
        except FieldDoesNotExist:
            raise ValueError("%s couldn't find a field named %s in %s." % \
                    (self.__class__.__name__, self.__field_name, self.model._meta.object_name))
        self.__is_validated = True
    
    def get_query_set(self):
        if not self.__is_validated:
            self._validate_field_name()
        return super(CurrentSiteProductManager, self).get_query_set().filter(**{self.__field_name + '__id__exact': settings.SITE_ID})
    

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
    
