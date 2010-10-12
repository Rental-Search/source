# -*- coding: utf-8 -*-
import datetime
import logbook
import random

from decimal import Decimal as D
from pyke import knowledge_engine
from urlparse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.products.models import CURRENCY, UNIT, Product
from eloue.products.utils import Enum
from eloue.rent.decorators import incr_sequence
from eloue.rent.fields import UUIDField, IntegerAutoField
from eloue.rent.manager import BookingManager
from eloue.rent.paypal import payments, PaypalError


BOOKING_STATE = Enum([
    (0, 'ASKED', _(u'Demandé')),
    (1, 'CANCELED', _(u'Annulé')),
    (2, 'PENDING', _(u'En attente')),
    (3, 'ONGOING', _(u'En cours')),
    (4, 'ENDED', _(u'Terminé')),
])

PAYMENT_STATE = Enum([
    (0, 'REJECTED', _(u'Rejeté')),
    (1, 'CANCELED_PENDING', _(u"En cours de d'annluation")),
    (2, 'CANCELED', _(u'Annulé')),
    (3, 'AUTHORIZED_PENDING', _(u"En cours d'autorisation")),
    (4, 'AUTHORIZED', _(u'Autorisé')),
    (5, 'HOLDED_PENDING', _(u'En cours de sequestration')),
    (6, 'HOLDED', _(u'Sequestré')),
    (7, 'PAID_PENDING', _(u'En cours de paiment')),
    (8, 'PAID', _(u'Payé')),
    (9, 'REFUNDED_PENDING', _(u'En attente de remboursement')),
    (10, 'REFUNDED', _(u'Remboursé')),
    (11, 'DEPOSIT_PENDING', _(u'Caution en cours de versement')),
    (12, 'DEPOSIT', _(u'Caution versée'))
])

COMMISSION = D(str(getattr(settings, 'COMMISSION', 0.1)))
INSURANCE_FEE = D(str(getattr(settings, 'INSURANCE_FEE', 0.0594)))
INSURANCE_COMMISSION = D(str(getattr(settings, 'INSURANCE_COMMISSION', 0)))
INSURANCE_TAXES = D(str(getattr(settings, 'INSURANCE_TAXES', 0.09)))

BOOKING_DAYS = getattr(settings, 'BOOKING_DAYS', 85)

PAYPAL_API_EMAIL = getattr(settings, 'PAYPAL_API_EMAIL')

PACKAGES_UNIT = {
    'hour':UNIT.HOUR,
    'week_end':UNIT.WEEK_END,
    'day':UNIT.DAY,
    'week':UNIT.WEEK,
    'two_weeks':UNIT.TWO_WEEKS,
    'month':UNIT.MONTH
}

PACKAGES = {
    UNIT.HOUR: lambda amount, delta: amount * (delta.seconds / 60), 
    UNIT.WEEK_END: lambda amount, delta: amount,
    UNIT.DAY: lambda amount, delta: amount * delta.days,
    UNIT.WEEK: lambda amount, delta: amount * delta.days,
    UNIT.TWO_WEEKS: lambda amount, delta: amount * delta.days,
    UNIT.MONTH: lambda amount, delta: amount * delta.days
}

log = logbook.Logger('eloue.rent')

class Booking(models.Model):
    """A reservation"""
    uuid = UUIDField(primary_key=True)
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    
    booking_state = models.IntegerField(default=BOOKING_STATE.ASKED, choices=BOOKING_STATE)
    payment_state = models.IntegerField(default=PAYMENT_STATE.AUTHORIZED_PENDING, choices=PAYMENT_STATE)
    
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    insurance_amount = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY)
    
    owner = models.ForeignKey(Patron, related_name='bookings')
    borrower = models.ForeignKey(Patron, related_name='rentals')
    product = models.ForeignKey(Product, related_name='bookings')
    
    contract_id = IntegerAutoField(db_index=True)
    pin = models.CharField(blank=True, max_length=4)
    ip = models.IPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(blank=True, editable=False)
    canceled_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    preapproval_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    pay_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    
    objects = BookingManager()
    
    @incr_sequence('contract_id', 'rent_booking_contract_id_seq')
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
            self.pin = str(random.randint(1000, 9999))
            self.deposit_amount = self.product.deposit_amount
            if self.product.has_insurance:
                self.insurance_amount = self.insurance_fee + self.insurance_taxes + self.insurance_commission
            else:
                self.insurance_amount = D(0)
        super(Booking, self).save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.owner == self.borrower:
            raise ValidationError(_(u"Un objet ne peut pas être louer à son propriétaire"))
        if self.started_at >= self.ended_at:
            raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))
        if self.total_amount < 0:
            raise ValidationError(_(u"Le prix total d'une location ne peut pas être négatif"))
        if (self.ended_at - self.started_at) > datetime.timedelta(days=BOOKING_DAYS):
            raise ValidationError(_(u"La durée d'une location est limitée à 85 jours."))
    
    @staticmethod
    def calculate_price(product, started_at, ended_at):
        delta = ended_at - started_at
        
        engine = knowledge_engine.engine((__file__, '.rules'))
        engine.activate('pricing')
        for price in product.prices.iterator():
            engine.assert_('prices', 'price', (price.unit, price.amount))
        vals, plans = engine.prove_1_goal('pricing.pricing($type, $started_at, $ended_at, $delta)', started_at=started_at, ended_at=ended_at, delta=delta)
        engine.reset()
        
        amount, unit = D(0), PACKAGES_UNIT[vals['type']]
        package = PACKAGES[unit]
        for price in product.prices.filter(unit=unit, started_at__isnull=True, ended_at__isnull=True):
            amount += package(price.amount, delta)
        
        for price in product.prices.filter(unit=unit, started_at__isnull=False, ended_at__isnull=False):
            amount += package(price.amount, price.delta(started_at, ended_at))
        
        return amount
    
    def preapproval(self, cancel_url=None, return_url=None, ip_address=None):
        """Preapprove payments for borrower from Paypal.
        
        Keywords arguments :
        cancel_url -- The URL to which the sender’s browser is redirected after the sender cancels the preapproval at paypal.com. 
        return_url -- The URL to which the sender’s browser is redirected after the sender approves the preapproval on paypal.com.
        ip_address -- The ip address of sender.
        
        The you should redirect user to :
        https://www.paypal.com/webscr?cmd=_ap-preapproval&preapprovalkey={{ preapproval_key }}
        """
        try:
            response = payments.preapproval(
                startingDate = datetime.datetime.now(),
                endingDate = self.ended_at,
                currencyCode = self.currency,
                maxTotalAmountOfAllPayments = str(self.total_amount + self.deposit_amount),
                cancelUrl = cancel_url,
                returnUrl = return_url,
                ipnNotificationUrl = urljoin(
                    "http://%s" % Site.objects.get_current().domain, reverse('preapproval_ipn')
                ),
                client_details = {
                    'ipAddress': ip_address,
                    'partnerName': 'e-loue',
                    'customerType': 'Business' if self.borrower.is_professional else 'Personnal',
                    'customerId': str(self.borrower.pk)
                }
            )
            if response['responseEnvelope']['ack'] in ['Success', 'SuccessWithWarning']:
                log.info("Preapproval accepted")
                self.payment_state = PAYMENT_STATE.AUTHORIZED
                self.preapproval_key = response['preapprovalKey']
            else:
                log.info("Preapproval rejected")
                self.payment_state = PAYMENT_STATE.REJECTED
        except PaypalError, e:
            log.error(e)
            self.payment_state = PAYMENT_STATE.REJECTED
        self.save()
    
    @property
    def commission(self):
        """Return our commission
        
        >>> booking = Booking(total_amount=10)
        >>> booking.commission
        Decimal('1.0')
        """
        return self.total_amount * COMMISSION
    
    @property
    def net_price(self):
        """Return net price for owner
        
        >>> booking = Booking(total_amount=10)
        >>> booking.net_price
        Decimal('9.0')
        """
        return self.total_amount - self.commission
    
    @property
    def insurance_commission(self):
        """Return our commission on insurance
        
        >>> booking = Booking(total_amount=10)
        >>> booking.insurance_commission
        Decimal('0')
        """
        return self.total_amount * INSURANCE_COMMISSION
    
    @property
    def insurance_fee(self):
        """Return insurance commission
        
        >>> booking = Booking(total_amount=10)
        >>> booking.insurance_fee
        Decimal('0.540')
        """
        return self.total_amount * INSURANCE_FEE
    
    @property
    def insurance_taxes(self):
        """Return insurance taxes
        
        >>> booking = Booking(total_amount=10)
        >>> booking.insurance_taxes
        Decimal('0.04860')
        """
        return self.insurance_fee * INSURANCE_TAXES
    
    def hold(self, cancel_url=None, return_url=None):
        """Take money from borrower and keep it safe for later.
        
        Keywords arguments :
        cancel_url -- The URL to which the sender’s browser is redirected after the sender cancels the preapproval at paypal.com. 
        return_url -- The URL to which the sender’s browser is redirected after the sender approves the preapproval on paypal.com.
        ip_address -- The ip address of sender.
        
        Then you should redirect user to : 
        https://www.paypal.com/webscr?cmd=_ap-payment&paykey={{ pay_key }}
        """
        try:
            response = payments.pay(
                # FIXME : Patron email might not be related to PayPal account
                senderEmail = self.borrower.email,
                actionType = 'PAY_PRIMARY',
                feesPayer = 'PRIMARYRECEIVER',
                cancelUrl = cancel_url,
                returnUrl = return_url,
                currencyCode = self.currency,
                preapprovalKey = self.preapproval_key,
                ipnNotificationUrl = urljoin(
                    "http://%s" % Site.objects.get_current().domain, reverse('pay_ipn')
                ),
                receiverList = { 'receiver': [
                    {'primary':True, 'amount':str(self.total_amount), 'email':PAYPAL_API_EMAIL},
                    {'primary':False, 'amount':str(self.net_price), 'email':self.owner.email }
                ]}
            )
            if response['paymentExecStatus'] in ['CREATED', 'INCOMPLETE']:
                self.payment_state = PAYMENT_STATE.HOLDED
            elif response['paymentExecStatus'] in ['PROCESSING', 'PENDING']:
                self.payment_state = PAYMENT_STATE.HOLDED_PENDING
            else: # FIXME : Hazardous, in this case only INCOMPLETE is the only valid response
                log.warn(response['paymentExecStatus'])
            self.pay_key = response['payKey']
        except PaypalError, e:
            log.error(e)
        self.save()
    
    def pay(self):
        """Return deposit_amount to borrower and pay the owner"""
        try:
            response = payments.execute_payment(
                payKey = self.pay_key
            )
            if response['paymentExecStatus'] in ['COMPLETED']:
                self.payment_state = PAYMENT_STATE.PAID
            else:
                self.payment_state = PAYMENT_STATE.PAID_PENDING
            self.save()
        except PaypalError, e:
            log.error(e)
    
    def cancel(self):
        """Cancel preapproval for the borrower"""
        try:
            response = payments.cancel_preapproval(
                preapprovalKey = self.preapproval_key,
            )
            if response['responseEnvelope']['ack'] in ["Success", "SuccessWithWarning"]:
                self.payment_state = PAYMENT_STATE.CANCELED
            else:
                self.payment_state = PAYMENT_STATE.CANCELED_PENDING
        except PaypalError, e:
            log.error(e)
        self.save()
    
    def litigation(self, amount=None, cancel_url='', return_url=''):
        """Giving caution to owner"""
        if not amount or amount > self.deposit_amount:
            amount = self.deposit_amount
        
        try:
            response = payments.pay(
                actionType = 'PAY',
                senderEmail = self.borrower.email,
                preapprovalKey = self.preapproval_key,
                cancelUrl = cancel_url,
                returnUrl = return_url,
                currencyCode = self.currency,
                ipnNotificationUrl = urljoin(
                    "http://%s" % Site.objects.get_current().domain, reverse('pay_ipn')
                ),
                receiverList = { 'receiver':[
                    {'amount':str(amount), 'email':self.owner.email},
                ]}
            )
            if response['paymentExecStatus'] in ['CREATED', 'COMPELTED']:
                self.payment_state = PAYMENT_STATE.DEPOSIT
            elif response['paymentExecStatus'] in ['PROCESSING', 'PENDING']:
                self.payment_state = PAYMENT_STATE.DEPOSIT_PENDING
            else:
                log.warn(response['paymentExecStatus'])
            self.save()
        except PaypalError, e:
            log.error(e)
    
    def refund(self):
        """Refund borrower or owner if something as gone wrong"""
        try:
            response = payments.refund(
                payKey = self.pay_key,
                currencyCode = self.currency
            )
            if response['refundStatus'] in ['REFUNDED', 'NOT_PAID', 'ALREADY_REVERSED_OR_REFUNDED']:
                self.payment_state = PAYMENT_STATE.REFUNDED
            else:
                self.payment_state = PAYMENT_STATE.REFUNDED_PENDING
            self.save()
        except PaypalError, e:
            log.error(e)
    

class Sinister(models.Model):
    uuid = UUIDField(primary_key=True)
    sinister_id = IntegerAutoField(db_index=True)
    description = models.TextField()
    patron = models.ForeignKey(Patron, related_name='sinisters')
    booking =  models.ForeignKey(Booking, related_name='sinisters')
    product = models.ForeignKey(Product, related_name='sinisters')
    
    created_at = models.DateTimeField(blank=True, editable=False)
    
    @incr_sequence('sinister_id', 'rent_sinister_sinister_id_seq')
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Sinister, self).save(*args, **kwargs)
    

