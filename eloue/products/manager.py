# -*- coding: utf-8 -*-
from django.db.models import Manager

class ProductManager(Manager):
    def active(self):
        return self.filter(is_archived=False, is_allowed=True)
    
    def archived(self):
        return self.filter(is_archived=True, is_allowed=True)
    

class QuestionManager(Manager):
    def drafts(self):
        from eloue.products.models import STATUS
        return self.get_query_set().filter(status=STATUS.DRAFT)
    
    def privates(self):
        from eloue.products.models import STATUS
        return self.get_query_set().filter(status=STATUS.PRIVATE)
    
    def public(self):
        from eloue.products.models import STATUS
        return self.get_query_set().filter(status=STATUS.PUBLIC)
    
    def removed(self):
        from eloue.products.models import STATUS
        return self.get_query_set().filter(status=STATUS.REMOVED)
    

