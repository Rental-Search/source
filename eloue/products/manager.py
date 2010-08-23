# -*- coding: utf-8 -*-
from django.db.models import Manager

class ProductManager(Manager):
    def active(self):
        return self.filter(is_archived=False, is_allowed=True)
    
    def archived(self):
        return self.filter(is_archived=True, is_allowed=True)
    
