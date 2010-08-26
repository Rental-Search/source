# -*- coding: utf-8 -*-
import datetime, random

from django.db import models
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.products.models import Product

BOOKING_STATE = (
    (0, _('Demander')),
    (1, _('Annuler')),
    (2, _('En attente')),
    (3, _('En cours')),
    (4, _('Terminer')),
)

PAYMENT_STATE = (
    (0, _('Autoriser')),
    (1, _('Payer'))
)

class Booking(models.Model):
    """A reservation"""
    started_at = models.DateTimeField(null=False)
    ended_at = models.DateTimeField(null=False)
    total_price = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    booking_state = models.IntegerField(null=False, choices=BOOKING_STATE)
    payment_state = models.IntegerField(null=False, choices=PAYMENT_STATE)
    owner = models.ForeignKey(Patron, related_name='bookings')
    borrower = models.ForeignKey(Patron, related_name='rentals')
    product = models.ForeignKey(Product, related_name='bookings')
    pin = models.CharField(unique=True, blank=True, null=False, max_length=4)
    created_at = models.DateTimeField(blank=True)
    ip = models.IPAddressField(blank=True, null=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.owner == self.borrower:
            raise ValidationError(_(u"Un objet ne peut pas être louer à son propriétaire"))
        if self.started_at >= self.ended_at:
            raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))
        if self.total_price < 0:
            raise ValidationError(_(u"Le prix total d'une location ne peut pas être négatif"))
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
            self.passphrase = str(random.randint(1000, 9999))
        super(Booking, self).save(*args, **kwargs)
    
