# -*- coding: utf-8 -*-
import types

from django.contrib.sites.managers import CurrentSiteManager
from django.db.models import Manager

from django.db.models.query import QuerySet

class ProBookingQuerySet(QuerySet):
    def get(self, *args, **kwargs):
        from rent.models import ProBooking, BOOKING_STATE
        instance = super(ProBookingQuerySet, self).get(*args, **kwargs)
        if instance.state == BOOKING_STATE.PROFESSIONAL or instance.state == BOOKING_STATE.PROFESSIONAL_SAW:
            return ProBooking(*[getattr(instance, field.attname) for field in instance._meta.fields])
        return instance


class BookingManager(Manager):
    def __init__(self):
        from rent.models import BOOKING_STATE
        super(BookingManager, self).__init__()
        for state in BOOKING_STATE.enum_dict:
            setattr(self, state.lower(), types.MethodType(self._filter_factory(state), self, BookingManager))
    
    @staticmethod
    def _filter_factory(state):
        from rent.models import BOOKING_STATE
        def filter(self, **kwargs):
            return super(BookingManager, self).filter(state=BOOKING_STATE[state], **kwargs)
        return filter

    def history(self):
        from rent.models import BOOKING_STATE
        return self.exclude(
            state__in=[
                BOOKING_STATE.ONGOING, 
                BOOKING_STATE.PENDING, 
                BOOKING_STATE.AUTHORIZED,
                BOOKING_STATE.AUTHORIZING,
                BOOKING_STATE.OUTDATED
            ]
        )

    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        return ProBookingQuerySet(self.model, using=self._db)


class CurrentSiteBookingManager(CurrentSiteManager, BookingManager):
    pass
