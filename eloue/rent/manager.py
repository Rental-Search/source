# -*- coding: utf-8 -*-
import types

from django.contrib.sites.managers import CurrentSiteManager
from django.db.models import Manager


class BookingManager(Manager):
    def __init__(self):
        from eloue.rent.models import BOOKING_STATE
        super(BookingManager, self).__init__()
        for state in BOOKING_STATE.enum_dict:
            setattr(self, state.lower(), types.MethodType(self._filter_factory(state), self, BookingManager))
    
    @staticmethod
    def _filter_factory(state):
        from eloue.rent.models import BOOKING_STATE
        def filter(self, **kwargs):
            return super(BookingManager, self).filter(state=BOOKING_STATE[state], **kwargs)
        return filter

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

    def get(self, *args, **kwargs):
        instance = super(BookingManager, self).get(*args, **kwargs)
        from eloue.rent.models import ProBooking, BOOKING_STATE
        if instance.state == BOOKING_STATE.PROFESSIONAL:
            return ProBooking(*[getattr(instance, field.attname) for field in instance._meta.fields])
        return instance

class CurrentSiteBookingManager(CurrentSiteManager, BookingManager):
    pass
