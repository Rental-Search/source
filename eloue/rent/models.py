# -*- coding: utf-8 -*-
import datetime, random

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from paypalx.payments import PaymentsAPI

from eloue.accounts.models import Patron
from eloue.products.models import Product
from eloue.products.utils import Enum

BOOKING_STATE = Enum(
    (0, 'ASKED', _(u'Demandé')),
    (1, 'CANCELED', _(u'Annulé')),
    (2, 'PENDING', _(u'En attente')),
    (3, 'ONGOING', _(u'En cours')),
    (4, 'ENDED', _(u'Terminé')),
)

PAYMENT_STATE = Enum(
    (0, 'REJECTED', _(u'Rejeté'))
    (1, 'AUTHORIZED', _(u'Autorisé')),
    (2, 'PAID', _(u'Payé')),
    (3, 'REFUNDED_PENDING', _(u'En attente de remboursement')),
    (4, 'REFUNDED', _(u'Remboursé')),
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
    
    preapproval_key = models.CharField(null=True, max_length=255)
    
    def preapproval(self, **kwargs):
        if self.payment_state != PAYMENT_STATE.AUTHORIZED:
            paypal = PaymentsAPI(settings.PAYPAL_API_USERNAME, settings.PAYPAL_API_PASSWORD, settings.PAYPAL_API_SIGNATURE, settings.PAYPAL_API_APPLICATION_ID, settings.PAYPAL_API_EMAIL)
            response = paypal.preapproval(
                startingDate = self.started_at,
                endingDate = self.ended_at,
                currencyCode = 'EUR', # FIXME : Hardcoded currency
                # TODO : Missing value
            )
            # TODO : Check return status and deal with it
    
    def refund(self):
        if self.payment_state != PAYMENT_STATE.REFUNDED:
            paypal = PaymentsAPI(settings.PAYPAL_API_USERNAME, settings.PAYPAL_API_PASSWORD, settings.PAYPAL_API_SIGNATURE, settings.PAYPAL_API_APPLICATION_ID, settings.PAYPAL_API_EMAIL)
            response = paypal.refund(
                trackingId = self.pk,
                currencyCode = 'EUR' # FIXME : Hardcoded currency
            )
            # TODO : Check return status and deal with it
            self.payment_state = PAYMENT_STATE.REFUNDED
            self.save()
    
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
            self.pin = str(random.randint(1000, 9999))
        super(Booking, self).save(*args, **kwargs)
    
