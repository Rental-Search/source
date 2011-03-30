# -*- coding: utf-8 -*-
from eloue.rent.payments.abstract_payment import AbstractPayment



class NonPayments(AbstractPayment):
    
    NOT_NEED_IPN = True
    
    def __init__(self, booking):
        self.booking = booking
        super(NonPayments, self).__init__()
        
        
    def preapproval(self, cancel_url=None, return_url=None, ip_address=None):
        self.booking.send_ask_email()
        return None
        

    def pay(self, cancel_url=None, return_url=None):
        return None
        
    def refund(self):
        pass
        
    def execute_payment(self):
        pass
        
    def cancel_preapproval(self):
        pass
        
    def give_caution(self, amount, cancel_url, return_url):
        pass
        