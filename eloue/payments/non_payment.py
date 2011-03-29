# -*- coding: utf-8 -*-
from eloue.payments.abstract_payment import AbstractPayment
import httplib, urllib
from django.core.urlresolvers import reverse


ELOUE_URL = "192.168.0.28:8000" # to change

class NonPayments(AbstractPayment):
    
    def __init__(self, booking):
        self.booking_pk = booking.pk.hex
        super(NonPayments, self).__init__()
        
        
    def preapproval(self, cancel_url, return_url, ip_address, domain, protocol, total_amount):
        """
        No need to reject the booking.
        """
        
        print "####### non payment preproval called ###########"
        params = urllib.urlencode({"booking_pk": self.booking_pk})
        print "###### pk hex #####", params
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(ELOUE_URL) 
        print "#### http con sucess ####"
        #conn.request("POST", '/booking/ipn/fakepreapproval', params, headers)
        conn.request("POST", reverse('fake_preapproval_ipn'), params, headers)
        print "#####  http request sucess #####"
        response = conn.getresponse()
        conn.close()
        print "###### http close #######"
        
        
    def pay(self, cancel_url, return_url, domain, protocol, total_amount, net_price):
        params = urllib.urlencode({"booking_pk": self.booking_pk})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(ELOUE_URL)
        #conn.request("POST", reverse('/booking/ipn/fakepay/'), params, headers)
        conn.request("POST", reverse('fake_pay_ipn'), params, headers)
        response = conn.getresponse()
        conn.close()
        
    def refund(self):
        pass
        
    def execute_payment(self):
        pass
        
    def cancel_preapproval(self):
        pass
        
    def give_caution(self):
        pass
        
        