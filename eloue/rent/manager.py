# -*- coding: utf-8 -*-
from django.db.models import Manager

class BookingManager(Manager):
    def asked(self):
        from eloue.rent.models import BOOKING_STATE
        return self.get_queryset().filter(booking_state=BOOKING_STATE.ASKED)
    
    def canceled(self):
        from eloue.rent.models import BOOKING_STATE
        return self.get_queryset().filter(booking_state=BOOKING_STATE.CANCELED)
    
    def pending(self):
        from eloue.rent.models import BOOKING_STATE
        return self.get_queryset().filter(booking_state=BOOKING_STATE.PENDING)
    
    def ongoing(self):
        from eloue.rent.models import BOOKING_STATE
        return self.get_queryset().filter(booking_state=BOOKING_STATE.ONGOING)
    
    def ended(self):
        from eloue.rent.models import BOOKING_STATE
        return self.get_queryset().filter(booking_state=BOOKING_STATE.ENDED)
    

