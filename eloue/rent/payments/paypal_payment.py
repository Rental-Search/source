# -*- coding: utf-8 -*-
from django.conf import settings
from paypalx import PaypalError, AdaptivePayments, AdaptiveAccounts
from eloue.rent.payments.abstract_payment import AbstractPayment
import datetime
from decimal import Decimal as D, ROUND_CEILING, ROUND_FLOOR
from urlparse import urljoin
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from eloue.utils import convert_from_xpf




__all__ = ['PaypalError', 'accounts']

accounts = AdaptiveAccounts(
    settings.PAYPAL_API_USERNAME,
    settings.PAYPAL_API_PASSWORD,
    settings.PAYPAL_API_SIGNATURE,
    settings.PAYPAL_API_APPLICATION_ID,
    settings.PAYPAL_API_EMAIL,
    sandbox=settings.USE_PAYPAL_SANDBOX
)



class AdaptivePapalPayments(AbstractPayment):
    

    NOT_NEED_IPN = False
    
    def __init__(self, booking):
        
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
        
    
    def preapproval(self, cancel_url, return_url, ip_address):

        now = datetime.datetime.now()
        domain = Site.objects.get_current().domain
        protocol = "https"
        total_amount = None
        if settings.CONVERT_XPF:
            total_amount = convert_from_xpf(self.booking.total_amount)
        else:
            total_amount = self.booking.total_amount
        return_url = "http://192.168.0.16:8000/dashboard/" #for test sake
        response = self.payments.preapproval(
            startingDate=now,
            endingDate=now + datetime.timedelta(days=360),
            currencyCode=self.booking._currency,
            maxTotalAmountOfAllPayments=str(total_amount.quantize(D(".00"), ROUND_CEILING)),
            cancelUrl=cancel_url,
            returnUrl=return_url,
            ipnNotificationUrl=urljoin("%s://%s" % (protocol, domain), reverse('preapproval_ipn')),
            client_details={
                'ipAddress': ip_address,
                'partnerName': 'e-loue',
                'customerType': 'Business' if self.booking.borrower.is_professional else 'Personnal',
                'customerId': str(self.booking.borrower.pk)
            }
        )
        return response['preapprovalKey']

        
    def pay(self, cancel_url, return_url):
        
        domain = Site.objects.get_current().domain
        protocol = "https"
        total_amount = None
        net_price = None
        return_url = "http://192.168.0.16:8000/dashboard/" #for test sake
        if settings.CONVERT_XPF:
            total_amount = convert_from_xpf(self.booking.total_amount)
            net_price = convert_from_xpf(self.booking.net_price)
        else:
            total_amount = self.booking.total_amount
            net_price = self.booking.net_price
        response = self.payments.pay(
            actionType='PAY_PRIMARY',
            senderEmail=self.booking.borrower.paypal_email,
            feesPayer='PRIMARYRECEIVER',
            cancelUrl=cancel_url,
            returnUrl=return_url,
            currencyCode=self.booking._currency,
            preapprovalKey=self.booking.preapproval_key,
            ipnNotificationUrl=urljoin("%s://%s" % (protocol, domain), reverse('pay_ipn')),
            receiverList={'receiver': [
                {'primary':True, 'amount':str(total_amount.quantize(D(".00"), ROUND_CEILING)), 'email':settings.PAYPAL_API_EMAIL},
                {'primary':False, 'amount':str(net_price.quantize(D(".00"), ROUND_FLOOR)), 'email':self.booking.owner.paypal_email}
            ]}
        )
        return response['payKey']

     
    def refund(self):
        response = self.payments.refund(
            payKey=self.booking.pay_key,
            currencyCode=self.booking._currency
        )
    
    def execute_payment(self):
        response = self.payments.execute_payment(
            payKey=self.booking.pay_key
        )
    
    def cancel_preapproval(self):
        response = self.payments.cancel_preapproval(
                preapprovalKey=self.booking.preapproval_key,
            )
        self.booking.canceled_at = datetime.datetime.now()
        
    def give_caution(self, amount, cancel_url, return_url):
        if not amount or amount > self.booking.deposit_amount:
            amount = self.booking.deposit_amount
        
        domain = Site.objects.get_current().domain
        protocol = "https"
            
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
    
    
    
    
    
    
    
    
    
    
    
    
        
        