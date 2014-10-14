# -*- coding: utf-8 -*-
import types

from django.contrib.sites.managers import CurrentSiteManager
from django.db.models import Manager

from django.db.models.query import QuerySet

from rent.choices import BOOKING_STATE

class ProBookingQuerySet(QuerySet):
    def get(self, *args, **kwargs):
        from rent.models import ProBooking
        instance = super(ProBookingQuerySet, self).get(*args, **kwargs)
        if instance.state in (BOOKING_STATE.PROFESSIONAL, BOOKING_STATE.PROFESSIONAL_SAW):
            return ProBooking(*[getattr(instance, field.attname) for field in instance._meta.fields])
        return instance


class BookingManager(Manager):
    def __init__(self):
        super(BookingManager, self).__init__()
        for state in BOOKING_STATE.enum_dict:
            setattr(self, state.lower(), types.MethodType(self._filter_factory(state), self, BookingManager))
    
    @staticmethod
    def _filter_factory(state):
        def _filter(self, **kwargs):
            return super(BookingManager, self).filter(state=BOOKING_STATE[state], **kwargs)
        return _filter

    def history(self):
        return self.exclude(
            state__in=[
                BOOKING_STATE.ONGOING, 
                BOOKING_STATE.PENDING, 
                BOOKING_STATE.AUTHORIZED,
                BOOKING_STATE.AUTHORIZING,
                BOOKING_STATE.OUTDATED
            ]
        )

    def active(self):
        return self.exclude(
            state__in=[
                BOOKING_STATE.AUTHORIZING,
                BOOKING_STATE.REFUNDED,
                BOOKING_STATE.DEPOSIT,
                BOOKING_STATE.CLOSING,
                BOOKING_STATE.UNACCEPTED,
                BOOKING_STATE.ACCEPTED_UNAUTHORIZED,
            ]
        )

    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        return ProBookingQuerySet(self.model, using=self._db)


class CurrentSiteBookingManager(CurrentSiteManager, BookingManager):
    pass


class CommentManager(Manager):
    def __init__(self, comment_type):
        super(CommentManager, self).__init__()
        self.comment_type = comment_type

    def get_query_set(self):
        qs = super(CommentManager, self).get_query_set()
        return qs.filter(type=self.comment_type)
