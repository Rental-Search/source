# -*- coding: utf-8 -*-

class PaymentException(Exception):
    pass

class AbstractPayment(object):
    
    def __init__(self, *args, **kwargs):
        pass
        
    def preapproval(self, cancel_url, return_url, ip_address):
        pass
        
    def pay(self, cancel_url, return_url):
        pass
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def give_caution(self, amount, cancel_url, return_url):
        pass
