# -*- coding: utf-8 -*-
import datetime
import logbook
import types
import random

from decimal import Decimal as D
from pyke import knowledge_engine
from urlparse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.products.models import CURRENCY, UNIT, Product
from eloue.products.utils import Enum
from eloue.rent.decorators import incr_sequence
from eloue.rent.fields import UUIDField, IntegerAutoField
from eloue.rent.manager import BookingManager
from eloue.paypal import payments, PaypalError
from eloue.utils import create_alternative_email

BOOKING_STATE = Enum([
    (0, 'ASKED', _(u'Demandé')),
    (1, 'REJECTED', _(u'Rejeté')),
    (2, 'CANCELED', _(u'Annulé')),
    (3, 'PENDING', _(u'En attente')),
    (4, 'ONGOING', _(u'En cours')),
    (5, 'ENDED', _(u'Terminé')),
    (6, 'INCIDENT', _(u'Incident')),
    (7, 'CLOSED', _(u'Cloturé')),
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
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)
PAYPAL_API_EMAIL = getattr(settings, 'PAYPAL_API_EMAIL')

PACKAGES_UNIT = {
    'hour': UNIT.HOUR,
    'week_end': UNIT.WEEK_END,
    'day': UNIT.DAY,
    'week': UNIT.WEEK,
    'two_weeks': UNIT.TWO_WEEKS,
    'month': UNIT.MONTH
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
    
    booking_state = models.PositiveSmallIntegerField(default=BOOKING_STATE.ASKED, choices=BOOKING_STATE)
    payment_state = models.PositiveSmallIntegerField(default=PAYMENT_STATE.AUTHORIZED_PENDING, choices=PAYMENT_STATE)
    
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    insurance_amount = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=CURRENCY.EUR)
    
    owner = models.ForeignKey(Patron, related_name='bookings')
    borrower = models.ForeignKey(Patron, related_name='rentals')
    product = models.ForeignKey(Product, related_name='bookings')
    
    contract_id = IntegerAutoField(unique=True, db_index=True)
    pin = models.CharField(blank=True, max_length=4)
    ip = models.IPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(blank=True, editable=False)
    canceled_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    preapproval_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    pay_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    
    objects = BookingManager()
    
    PAYMENT_STATE = PAYMENT_STATE
    BOOKING_STATE = BOOKING_STATE
    
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
        if self.started_at and self.ended_at:
            if self.started_at <= datetime.datetime.now() or self.ended_at <= datetime.datetime.now():
                raise ValidationError(_(u"Vous ne pouvez pas louer a ces dates"))
            if self.started_at >= self.ended_at:
                raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))
            if (self.ended_at - self.started_at) > datetime.timedelta(days=BOOKING_DAYS):
                raise ValidationError(_(u"La durée d'une location est limitée à 85 jours."))
    
    @permalink
    def get_absolute_url(self):
        return ('booking_detail', [self.pk.hex])
    
    def __init__(self, *args, **kwargs):
        super(Booking, self).__init__(*args, **kwargs)
        for state in BOOKING_STATE.enum_dict:
            setattr(self, "is_%s" % state.lower(), types.MethodType(self._is_factory(state), self))
    
    @staticmethod
    def _is_factory(state):
        def is_state(self):
            return self.booking_state == getattr(BOOKING_STATE, state)
        return is_state
        
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
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        try:
            now = datetime.datetime.now()
            response = payments.preapproval(
                startingDate=now,
                endingDate=now + datetime.timedelta(days=360),
                currencyCode=self.currency,
                maxTotalAmountOfAllPayments=str(self.total_amount + self.deposit_amount),
                cancelUrl=cancel_url,
                returnUrl=return_url,
                ipnNotificationUrl=urljoin(
                    "%s://%s" % (protocol, domain), reverse('preapproval_ipn')
                ),
                client_details={
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
    
    def send_ask_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_ask', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_ask', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    def send_acceptation_email(self):
        from eloue.rent.contract import ContractGenerator
        context = {'booking': self}
        contract_generator = ContractGenerator()
        contract = contract_generator(self)
        content = contract.getvalue()
        message = create_alternative_email('rent/emails/owner_acceptation', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.attach('contrat.pdf', content, 'application/pdf')
        message.send()
        message = create_alternative_email('rent/emails/borrower_acceptation', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.attach('contrat.pdf', content, 'application/pdf')
        message.send()
    
    def send_rejection_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/borrower_rejection', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
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
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        try:
            response = payments.pay(
                actionType='PAY_PRIMARY',
                senderEmail=self.borrower.paypal_email,
                feesPayer='PRIMARYRECEIVER',
                cancelUrl=cancel_url,
                returnUrl=return_url,
                currencyCode=self.currency,
                preapprovalKey=self.preapproval_key,
                ipnNotificationUrl=urljoin(
                    "%s://%s" % (protocol, domain), reverse('pay_ipn')
                ),
                receiverList={'receiver': [
                    {'primary':True, 'amount':str(self.total_amount), 'email':PAYPAL_API_EMAIL},
                    {'primary':False, 'amount':str(self.net_price), 'email':self.owner.email}
                ]}
            )
            if response['paymentExecStatus'] in ['CREATED', 'INCOMPLETE']:
                self.payment_state = PAYMENT_STATE.HOLDED
            elif response['paymentExecStatus'] in ['PROCESSING', 'PENDING']:
                self.payment_state = PAYMENT_STATE.HOLDED_PENDING
            else:  # FIXME : Hazardous, in this case only INCOMPLETE is the only valid response
                log.warn(response['paymentExecStatus'])
            self.pay_key = response['payKey']
        except PaypalError, e:
            log.error(e)
        self.save()
    
    def pay(self):
        """Return deposit_amount to borrower and pay the owner"""
        try:
            response = payments.execute_payment(
                payKey=self.pay_key
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
                preapprovalKey=self.preapproval_key,
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
        
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
        try:
            response = payments.pay(
                actionType='PAY',
                senderEmail=self.borrower.paypal_email,
                preapprovalKey=self.preapproval_key,
                cancelUrl=cancel_url,
                returnUrl=return_url,
                currencyCode=self.currency,
                ipnNotificationUrl=urljoin(
                    "%s://%s" % (protocol, domain), reverse('pay_ipn')
                ),
                receiverList={'receiver': [
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
                payKey=self.pay_key,
                currencyCode=self.currency
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
    sinister_id = IntegerAutoField(unique=True, db_index=True)
    description = models.TextField()
    patron = models.ForeignKey(Patron, related_name='sinisters')
    booking = models.ForeignKey(Booking, related_name='sinisters')
    product = models.ForeignKey(Product, related_name='sinisters')
    
    created_at = models.DateTimeField(blank=True, editable=False)
    
    @incr_sequence('sinister_id', 'rent_sinister_sinister_id_seq')
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Sinister, self).save(*args, **kwargs)
    

