# -*- coding: utf-8 -*-
from django.conf import settings
from paypalx import PaypalError, AdaptivePayments, AdaptiveAccounts
from eloue.payments.abstract_payment import AbstractPayment
import datetime
from decimal import Decimal as D, ROUND_CEILING, ROUND_FLOOR
from urlparse import urljoin
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from eloue.utils import convert_from_xpf
import logbook
log = logbook.Logger('eloue.accounts')



__all__ = ['PaypalError', 'accounts']

accounts = AdaptiveAccounts(
    settings.PAYPAL_API_USERNAME,
    settings.PAYPAL_API_PASSWORD,
    settings.PAYPAL_API_SIGNATURE,
    settings.PAYPAL_API_APPLICATION_ID,
    settings.PAYPAL_API_EMAIL,
    sandbox=settings.USE_PAYPAL_SANDBOX
)


def verify_paypal_account(email, first_name, last_name):
    try:
        response = accounts.get_verified_status(
            emailAddress=email,
            firstName=first_name, 
            lastName=last_name, 
            matchCriteria="NAME"
            )
        return response['accountStatus']
    except PaypalError, e:
        log.error(e)
        return "INVALID"

class AdaptivePapalPayments(AbstractPayment):
    

    NOT_NEED_IPN = False
    
    def __init__(self, *args, **kwargs):
        
        self.payments = AdaptivePayments(
            settings.PAYPAL_API_USERNAME,
            settings.PAYPAL_API_PASSWORD,
            settings.PAYPAL_API_SIGNATURE,
            settings.PAYPAL_API_APPLICATION_ID,
            settings.PAYPAL_API_EMAIL,
            sandbox=settings.USE_PAYPAL_SANDBOX
        )
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
        response = self.payments.preapproval(
            startingDate=now,
            endingDate=now + datetime.timedelta(days=360),
            currencyCode=self.booking._currency,
            maxTotalAmountOfAllPayments=str(total_amount.quantize(D(".00"), ROUND_CEILING)),
            cancelUrl=cancel_url,
            returnUrl=return_url,
            ipnNotificationUrl='http://www.postbin.org/1fi02go' if settings.USE_PAYPAL_SANDBOX \
                else urljoin("%s://%s" % (protocol, domain), reverse('preapproval_ipn')),
            client_details={
                'ipAddress': ip_address,
                'partnerName': 'e-loue',
                'customerType': 'Business' if self.booking.borrower.is_professional else 'Personnal',
                'customerId': str(self.booking.borrower.pk)
            }
        )
        self.preapproval_key = response['preapprovalKey']

        
    def pay(self, cancel_url, return_url):
        # debit borrower
        domain = Site.objects.get_current().domain
        protocol = "https"

        total_amount = None
        net_price = None
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
            preapprovalKey=self.preapproval_key,
            ipnNotificationUrl='http://www.postbin.org/1fi02go' if settings.USE_PAYPAL_SANDBOX \
                else urljoin("%s://%s" % (protocol, domain), reverse('pay_ipn')),
            receiverList={'receiver': [
                {'primary':True, 'amount':str(total_amount.quantize(D(".00"), ROUND_CEILING)), 'email':settings.PAYPAL_API_EMAIL},
                {'primary':False, 'amount':str(net_price.quantize(D(".00"), ROUND_FLOOR)), 'email':self.booking.owner.paypal_email}
            ]}
        )
        if 'ERROR' in response.get('paymentExecStatus', None):
            PaypalError('paymentExecStatus' ,response.get('paymentExecStatus', None), response)
        self.pay_key = response['payKey']

     
    def refund(self):
        response = self.payments.refund(
            payKey=self.booking.pay_key,
            currencyCode=self.booking._currency
        )
    
    def execute_payment(self):
        # pay owner
        response = self.payments.execute_payment(
            payKey=self.booking.payment.pay_key
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
            ipnNotificationUrl='http://www.postbin.org/1fi02go' if settings.USE_PAYPAL_SANDBOX \
                else urljoin("%s://%s" % (protocol, domain), reverse('pay_ipn')),
            receiverList={'receiver': [
                {'amount':str(amount.quantize(D('.00'), ROUND_FLOOR)), 'email':self.booking.owner.paypal_email},
            ]}
        )

app = AdaptivePapalPayments(None)
    
def confirm_paypal_account(email):
    try:
        # try a test payment
        app.payments.pay(
          returnUrl='http://e-loue.com', 
          cancelUrl='http://e-loue.com', 
          actionType='PAY', 
          currencyCode='EUR', 
          receiverList={
            'receiver': [
              {
                'email': email, 
                'amount': '0.01', 
                'primary': False
              }, {
                'email': settings.PAYPAL_API_EMAIL,
                'amount': '0.01', 
                'primary': True
              }
            ]
          }
        )
        return True
    except PaypalError as e:
        # 569042 The email account is not confirmed by PayPal, 
        # or 'restricted' (probably means it's not existing)
        # or empty
        #if e.code == '569042' or e.code == '520009' or e.code == '580022':
        #   return False
        #else: raise
        return False
