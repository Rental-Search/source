# -*- coding: utf-8 -*-
import datetime

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
    owner = models.ForeignKey(Patron, related_name='sellings')
    borrower = models.ForeignKey(Patron, related_name='buyings')
    product = models.ForeignKey(Product, related_name='bookings')
    passphrase = models.CharField(unique=True, null=False, max_length=40)
    created_at = models.DateTimeField()
    ip = models.IPAddressField(null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Booking, self).save(*args, **kwargs)
    
