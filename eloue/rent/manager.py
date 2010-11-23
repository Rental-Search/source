# -*- coding: utf-8 -*-
import types

from django.db.models import Manager


class BookingManager(Manager):
    def __init__(self):
        from eloue.rent.models import BOOKING_STATE
        
        super(BookingManager, self).__init__()
        for state in BOOKING_STATE.enum_dict:
            setattr(self, state.lower(), types.MethodType(self._filter_factory(state), self))
    
    @staticmethod
    def _filter_factory(state):
        from eloue.rent.models import BOOKING_STATE
        
        def filter(self):
            return self.get_query_set().filter(state=BOOKING_STATE[state])
        return filter
    
