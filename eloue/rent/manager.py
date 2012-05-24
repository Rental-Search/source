# -*- coding: utf-8 -*-
import types

from django.contrib.sites.managers import CurrentSiteManager
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


    def authorized(self):
        return self.filter(state=BOOKING_STATE.AUTHORIZED)
    def pending(self):
        return self.filter(state=BOOKING_STATE.PENDING)
    def ongoing(self):
        return self.filter(state=BOOKING_STATE.ONGOING)
    def history(self):
        from eloue.rent.models import BOOKING_STATE
        return self.exclude(
            state__in=[
                BOOKING_STATE.ONGOING, 
                BOOKING_STATE.PENDING, 
                BOOKING_STATE.AUTHORIZED,
                BOOKING_STATE.AUTHORIZING,
                BOOKING_STATE.OUTDATED
            ]
        )
class CurrentSiteBookingManager(CurrentSiteManager, BookingManager):
    pass
