# -*- coding: utf-8 -*-
import datetime, logging, random, warnings

from urlparse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.products.models import CURRENCY, Product
from eloue.products.utils import Enum
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
    (1, 'AUTHORIZED', _(u'Autorisé')),
    (2, 'HOLDED_PENDING', _(u'En cours de sequestration')),
    (3, 'HOLDED', _(u'Sequestré')),
    (4, 'PAID_PENDING', _(u'En cours de paiment')),
    (5, 'PAID', _(u'Payé')),
    (6, 'REFUNDED_PENDING', _(u'En attente de remboursement')),
    (7, 'REFUNDED', _(u'Remboursé')),
])

FEE_PERCENTAGE = getattr(settings, 'FEE_PERCENTAGE', 0.1)

log = logging.getLogger(__name__)

class Booking(models.Model):
    """A reservation"""
    started_at = models.DateTimeField(null=False)
    ended_at = models.DateTimeField(null=False)
    total_price = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    currency = models.CharField(null=False, max_length=3, choices=CURRENCY)
    booking_state = models.IntegerField(null=False, default=BOOKING_STATE.ASKED, choices=BOOKING_STATE)
    payment_state = models.IntegerField(null=True, choices=PAYMENT_STATE)
    owner = models.ForeignKey(Patron, related_name='bookings')
    borrower = models.ForeignKey(Patron, related_name='rentals')
    product = models.ForeignKey(Product, related_name='bookings')
    pin = models.CharField(unique=True, blank=True, null=False, max_length=4)
    created_at = models.DateTimeField(blank=True)
    ip = models.IPAddressField(blank=True, null=True)
    
    preapproval_key = models.CharField(null=True, max_length=255)
    pay_key = models.CharField(null=True, max_length=255)
    
    def preapproval(self, cancel_url=None, return_url=None, ip_address=None):
        """
        Preapprove payments for borrower from Paypal.
        
        Keywords arguments :
        cancel_url -- The URL to which the sender’s browser is redirected after the sender cancels the preapproval at paypal.com. 
        return_url -- The URL to which the sender’s browser is redirected after the sender approves the preapproval on paypal.com.
        ip_address -- The ip address of sender.
        
        The you should redirect user to :
        https://www.paypal.com/webscr?cmd=_ap-preapproval&preapprovalkey={{ preapproval_key }}
        """
        if self.payment_state != PAYMENT_STATE.AUTHORIZED:
            try:
                response = payments.preapproval(
                    # FIXME : Patron email might not be related to PayPal account
                    senderEmail = self.borrower.email,
                    startingDate = datetime.datetime.now(),
                    endingDate = self.ended_at,
                    currencyCode = self.currency,
                    maxTotalAmountOfAllPayments = str(self.total_price),
                    cancelUrl = cancel_url,
                    returnUrl = return_url,
                    ipnNotificationUrl = urljoin(
                        "http://%s" % Site.objects.get_current().domain, reverse('ipn_handler')
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
    def fee(self):
        return (self.total_price * FEE_PERCENTAGE)
    
    @property
    def net_price(self):
        return self.total_price - self.fee
    
    def hold(self, cancel_url=None, return_url=None):
        """
        Take money from borrower and keep it safe for later.
        
        Keywords arguments :
        cancel_url -- The URL to which the sender’s browser is redirected after the sender cancels the preapproval at paypal.com. 
        return_url -- The URL to which the sender’s browser is redirected after the sender approves the preapproval on paypal.com.
        ip_address -- The ip address of sender.
        
        Then you should redirect user to : 
        https://www.paypal.com/webscr?cmd=_ap-payment&paykey={{ pay_key }}
        """
        if self.payment_state != PAYMENT_STATE.HOLDED:
            try:
                payments.debug = True
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
                        "http://%s" % Site.objects.get_current().domain, reverse('ipn_handler')
                    ),
                    trackingId = str(self.pk),
                    receiverList = { 'receiver': [
                        {'primary':True, 'amount':str(self.fee) , 'email':settings.PAYPAL_API_EMAIL },
                        {'amount':str(self.net_price), 'email':self.owner.email }
                    ]}
                )
                if response['paymentExecStatus'] in ['CREATED', 'INCOMPLETE']:
                    log.info("Payment was a success")
                    self.payment_state = PAYMENT_STATE.HOLDED
                elif response['paymentExecStatus'] in ['PROCESSING', 'PENDING']:
                    log.info("Payment was a failure")
                    self.payment_state = PAYMENT_STATE.HOLDED_PENDING
                else:
                    log.warn(response['paymentExecStatus'])
                self.pay_key = response['payKey']
            except PaypalError, e:
                log.error(e)
            self.save()
    
    def pay(self):
        if self.payment_state != PAYMENT_STATE.PAID:
            try:
                response = payments.execute_payment(
                    payKey = self.pay_key
                )
                if response['paymentExecStatus'] in ['COMPLETED']:
                    self.payment_state = PAYMENT_STATE.PAID
                else:
                    self.payment_state = PAYMENT_STATE.PAID_PENDING
                self.save()
                return True
            except PaypalError, e:
                return False # TODO : Add logging
    
    def refund(self):
        # FIXME : Not that much deprecated, just purely unfinished
        warnings.warn("deprecated", DeprecationWarning) 
        if self.payment_state != PAYMENT_STATE.REFUNDED:
            response = payments.refund(
                payKey = self.pay_key,
                trackingId = str(self.pk),
                currencyCode = self.currency
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
    
