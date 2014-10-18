# -*- coding: utf-8 -*-
from django.db.models import get_model
from payments.abstract_payment import AbstractPayment


class NonPayments(AbstractPayment):
    
    NOT_NEED_IPN = True
        
    def preapproval(self, *args, **kwargs):
        pass

    def pay(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def give_caution(self, *args, **kwargs):
        pass

    @property
    def creditcard(self):
        model = get_model('accounts', 'CreditCard')
        return model(expires='0000', masked_number='1XXXXXXXXXXXX234', holder_name='John Doe')
