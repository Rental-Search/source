# -*- coding: utf-8 -*-
import types

from django.db.models import Manager

class ProductManager(Manager):
    def active(self):
        return self.filter(is_archived=False, is_allowed=True)
    
    def archived(self):
        return self.filter(is_archived=True, is_allowed=True)
    

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
    

