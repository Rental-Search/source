# -*- coding: utf-8 -*-


class AbstractPayment(object):
    
    def __init__(self, *args, **kwargs):
        pass
        
    def preapproval(self, *args, **kwargs):
        pass
        
    def pay(self, *args, **kwargs):
        pass
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def give_caution(self, *args, **kwargs):
        pass
