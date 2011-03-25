# -*- coding: utf-8 -*-
from django.conf import settings
from paypalx import PaypalError, AdaptivePayments, AdaptiveAccounts
from eloue.payments.abstract_payment import AbstractPayment
import datetime
from decimal import Decimal as D, ROUND_CEILING, ROUND_FLOOR
from urlparse import urljoin
from django.core.urlresolvers import reverse

__all__ = ['PaypalError', 'accounts', 'payments']

accounts = AdaptiveAccounts(
    settings.PAYPAL_API_USERNAME,
    settings.PAYPAL_API_PASSWORD,
    settings.PAYPAL_API_SIGNATURE,
    settings.PAYPAL_API_APPLICATION_ID,
    settings.PAYPAL_API_EMAIL,
    sandbox=settings.USE_PAYPAL_SANDBOX
)

"""
payments = AdaptivePayments(
    settings.PAYPAL_API_USERNAME,
    settings.PAYPAL_API_PASSWORD,
    settings.PAYPAL_API_SIGNATURE,
    settings.PAYPAL_API_APPLICATION_ID,
    settings.PAYPAL_API_EMAIL,
    sandbox=settings.USE_PAYPAL_SANDBOX
)
"""

class AdaptivePapalPayments(AbstractPayment):
    
    def __init__(self, booking):
        print "paypal instanceed #####"
        self.payments = AdaptivePayments(
            settings.PAYPAL_API_USERNAME,
            settings.PAYPAL_API_PASSWORD,
            settings.PAYPAL_API_SIGNATURE,
            settings.PAYPAL_API_APPLICATION_ID,
            settings.PAYPAL_API_EMAIL,
            sandbox=settings.USE_PAYPAL_SANDBOX
        )
        self.booking = booking
        super(AdaptivePapalPayments, self).__init__()
    
    def preapproval(self, cancel_url, return_url, ip_address, domain, protocol, total_amount):
        print "####papal preapproval method called###"
        now = datetime.datetime.now()
        response = self.payments.preapproval(
            startingDate=now,
            endingDate=now + datetime.timedelta(days=360),
            currencyCode=self.booking._currency,
            maxTotalAmountOfAllPayments=str(total_amount.quantize(D(".00"), ROUND_CEILING)),
            cancelUrl=cancel_url,
            returnUrl=return_url,
            ipnNotificationUrl=urljoin(
                "%s://%s" % (protocol, domain), reverse('preapproval_ipn')
            ),
            client_details={
                'ipAddress': ip_address,
                'partnerName': 'e-loue',
                'customerType': 'Business' if self.booking.borrower.is_professional else 'Personnal',
                'customerId': str(self.booking.borrower.pk)
            }
        )
        self.booking.preapproval_key = response['preapprovalKey']
        
    def pay(self, cancel_url, return_url, domain, protocol, total_amount, net_price):
        print "##########paypal pay method called#############"
        response = self.payments.pay(
            actionType='PAY_PRIMARY',
            senderEmail=self.booking.borrower.paypal_email,
            feesPayer='PRIMARYRECEIVER',
            cancelUrl=cancel_url,
            returnUrl=return_url,
            currencyCode=self.booking._currency,
            preapprovalKey=self.booking.preapproval_key,
            ipnNotificationUrl=urljoin(
                "%s://%s" % (protocol, domain), reverse('pay_ipn')
            ),
            receiverList={'receiver': [
                {'primary':True, 'amount':str(total_amount.quantize(D(".00"), ROUND_CEILING)), 'email':PAYPAL_API_EMAIL},
                {'primary':False, 'amount':str(net_price.quantize(D(".00"), ROUND_FLOOR)), 'email':self.owner.paypal_email}
            ]}
        )
        self.booking.pay_key = response['payKey']
     
    def refund(self):
        print "##########paypal refund method called#############"
        response = self.payments.refund(
            payKey=self.booking.pay_key,
            currencyCode=self.booking._currency
        )
    
    def execute_payment(self):
        print "##########paypal execute method called#############"
        response = self.payments.execute_payment(
            payKey=self.booking.pay_key
        )
    
    def cancel_preapproval(self):
        print "##########paypal cancel method called#############"
        response = self.payments.cancel_preapproval(
                preapprovalKey=self.booking.preapproval_key,
            )
        self.booking.canceled_at = datetime.datetime.now()
        
    def give_caution(self):
        print "##########paypal give caution method called#############"
        response = self.payments.pay(
            actionType='PAY',
            senderEmail=self.booking.borrower.paypal_email,
            preapprovalKey=self.booking.preapproval_key,
            cancelUrl=cancel_url,
            returnUrl=return_url,
            currencyCode=self.booking._currency,
            ipnNotificationUrl=urljoin(
                "%s://%s" % (protocol, domain), reverse('pay_ipn')
            ),
            receiverList={'receiver': [
                {'amount':str(amount.quantize(D('.00'), ROUND_FLOOR)), 'email':self.booking.owner.paypal_email},
            ]}
        )
    
    
    
    
    
    
    
    
    
    
    
    
        
        