# -*- coding: utf-8 -*-
from eloue.payments.abstract_payment import AbstractPayment

class NonPayments(AbstractPayment):
    
    def __init__(self, booking):
        super(NonPayments, self).__init__()
        
    def preapproval(self, cancel_url, return_url, ip_address, domain, protocol, total_amount):
        pass
        
    def pay(self, cancel_url, return_url, domain, protocol, total_amount, net_price):
        pass
        
    def refund(self):
        pass
        
    def execute_payment(self):
        pass
        
    def cancel_preapproval(self):
        pass
        
    def give_caution(self):
        pass