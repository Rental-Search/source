# -*- coding: utf-8 -*-
import datetime
import logbook
import types
import random
import urllib

from decimal import Decimal as D, ROUND_CEILING, ROUND_FLOOR
from fsm.fields import FSMField
from fsm import transition
from pyke import knowledge_engine
from urlparse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.utils.formats import get_format
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.products.models import CURRENCY, UNIT, Product
from eloue.products.utils import Enum
from eloue.rent.decorators import incr_sequence
from eloue.rent.fields import UUIDField, IntegerAutoField
from eloue.rent.manager import BookingManager
from eloue.paypal import payments, PaypalError
from eloue.signals import post_save_sites
from eloue.utils import create_alternative_email

BOOKING_STATE = Enum([
    ('authorizing', 'AUTHORIZING', _(u"En cours d'autorisation")),
    ('authorized', 'AUTHORIZED', _(u"En attente")),
    ('rejected', 'REJECTED', _(u'Rejeté')),
    ('canceled', 'CANCELED', _(u'Annulé')),
    ('pending', 'PENDING', _(u'A venir')),
    ('ongoing', 'ONGOING', _(u'En cours')),
    ('ended', 'ENDED', _(u'Terminé')),
    ('incident', 'INCIDENT', _(u'Incident')),
    ('refunded', 'REFUNDED', _(u'Remboursé')),
    ('deposit', 'DEPOSIT', _(u'Caution versée')),
    ('closing', 'CLOSING', _(u"En attende de clôture")),
    ('closed', 'CLOSED', _(u'Clôturé')),
    ('outdated', 'OUTDATED', _(u"Dépassé"))
])

DEFAULT_CURRENCY = get_format('CURRENCY')

COMMISSION = D(str(getattr(settings, 'COMMISSION', 0.15)))
INSURANCE_FEE = D(str(getattr(settings, 'INSURANCE_FEE', 0.0594)))
INSURANCE_COMMISSION = D(str(getattr(settings, 'INSURANCE_COMMISSION', 0)))
INSURANCE_TAXES = D(str(getattr(settings, 'INSURANCE_TAXES', 0.09)))

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
    
    state = FSMField(default='authorizing', choices=BOOKING_STATE)
    
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=DEFAULT_CURRENCY)
    
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
    
    sites = models.ManyToManyField(Site, related_name='bookings')
    
    on_site = CurrentSiteManager()
    objects = BookingManager()
    
    STATE = BOOKING_STATE
    
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
    
    @permalink
    def get_absolute_url(self):
        return ('booking_detail', [self.pk.hex])
    
    def __unicode__(self):
        return self.product.summary
    
    def __init__(self, *args, **kwargs):
        super(Booking, self).__init__(*args, **kwargs)
        for state in BOOKING_STATE.enum_dict:
            setattr(self, "is_%s" % state.lower(), types.MethodType(self._is_factory(state), self))
    
    @staticmethod
    def _is_factory(state):
        def is_state(self):
            return self.state == getattr(BOOKING_STATE, state)
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
        
        return unit, amount
    
    @transition(source='authorizing', target='authorized')
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
                maxTotalAmountOfAllPayments=str(self.total_amount.quantize(D(".00"), ROUND_CEILING)),
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
            self.preapproval_key = response['preapprovalKey']
        except PaypalError, e:
            self.state = BOOKING_STATE.REJECTED
            log.error(e)
        self.save()
    
    def send_recovery_email(self):
        context = {
            'booking': self,
            'preapproval_url': settings.PAYPAL_COMMAND % urllib.urlencode({
                'cmd': '_ap-preapproval',
                'preapprovalkey': self.preapproval_key
            })
        }
        message = create_alternative_email('rent/emails/borrower_recovery', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
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
    
    def send_cancelation_email(self, source=None):
        context = {'booking': self}
        if self.owner == source:
            message = create_alternative_email('rent/emails/owner_cancelation_to_owner', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
            message.send()
            message = create_alternative_email('rent/emails/owner_cancelation_to_borrower', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
            message.send()
        else:
            message = create_alternative_email('rent/emails/borrower_cancelation_to_owner', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
            message.send()
            message = create_alternative_email('rent/emails/borrower_cancelation_to_borrower', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
            message.send()
    
    def send_ended_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_ended', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_ended', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    def send_closed_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_closed', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_closed', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    @property
    def commission(self):
        """Return our commission
        
        >>> booking = Booking(total_amount=10)
        >>> booking.commission
        Decimal('1.50')
        """
        return self.total_amount * COMMISSION
        
    @property
    def total_commission(self):
        """ Return all the commission
        
        >>> booking = Booking(total_amount=10)
        >>> booking.total_commission
        Decimal('2.040')
        """
        return self.commission + self.insurance_fee
    
    @property
    def net_price(self):
        """Return net price for owner
        
        >>> booking = Booking(total_amount=10)
        >>> booking.net_price
        Decimal('8.50')
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
    
    @transition(source='pending', target='ongoing')
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
                {'primary':True, 'amount':str(self.total_amount.quantize(D(".00"), ROUND_CEILING)), 'email':PAYPAL_API_EMAIL},
                {'primary':False, 'amount':str(self.net_price.quantize(D(".00"), ROUND_FLOOR)), 'email':self.owner.paypal_email}
            ]}
        )
        self.pay_key = response['payKey']
        self.save()
    
    @transition(source='ended', target='closing', save=True)
    def pay(self):
        """Return deposit_amount to borrower and pay the owner"""
        response = payments.execute_payment(
            payKey=self.pay_key
        )
    
    @transition(source=['authorized', 'pending'], target='canceled', save=True)
    def cancel(self):
        """Cancel preapproval for the borrower"""
        response = payments.cancel_preapproval(
            preapprovalKey=self.preapproval_key,
        )
        self.canceled_at = datetime.datetime.now()
    
    @transition(source='incident', target='deposit', save=True)
    def litigation(self, amount=None, cancel_url='', return_url=''):
        """Giving caution to owner"""
        # FIXME : Deposit amount isn't considered in preapproval amount
        if not amount or amount > self.deposit_amount:
            amount = self.deposit_amount
        
        domain = Site.objects.get_current().domain
        protocol = "https" if USE_HTTPS else "http"
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
                {'amount':str(amount.quantize(D('.00'), ROUND_FLOOR)), 'email':self.owner.paypal_email},
            ]}
        )
    
    @transition(source='incident', target='refunded', save=True)
    def refund(self):
        """Refund borrower or owner if something as gone wrong"""
        response = payments.refund(
            payKey=self.pay_key,
            currencyCode=self.currency
        )
    

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
    

post_save.connect(post_save_sites, sender=Booking)
