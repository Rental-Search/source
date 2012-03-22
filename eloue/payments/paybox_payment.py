# -*- coding: utf-8 -*-
import httplib, urllib
import contextlib
from decimal import Decimal as D

import abstract_payment
import datetime
import random
LENGTH=5
from urlparse import urlparse, parse_qs

permanent_data = {
    'VERSION': '00104',
    'DATEQ': datetime.datetime.now().strftime("%d%m%Y%H%M%S"),
    'NUMQUESTION': random.randint(10**(LENGTH-1),10**LENGTH-1), # <- NOT FOR PRODUCTION
    'SITE': 1999888,
    'RANG': 99,
    'CLE': '1999888I',
    'DEVISE': 978,
    'ACTIVITE': '024',
}

TYPE = {
    'AUTHORIZE': 1,
    'DEBIT': 2,
    'AUTHORIZE_DEBIT': 3,
    'CREDIT': 4,
    'CANCEL': 5,
    'FORCAGE': 12,
    'CHANGE_TRANSACTION_AMOUNT': 13,
    'REFUND': 14,
    'CONSULT': 17,  
    'SUBSCRIBER_AUTHORIZE': 51,
    'SUBSCRIBER_DEBIT': 52,
    'SUBSCRIBER_AUTHORIZE_DEBIT': 53,
    'SUBSCRIBER_CREDIT': 54,
    'SUBSCRIBER_CANCEL': 55,
    'SUBSCRIBER_SUBSCRIBE': 56,
    'SUBSCRIBER_MODIFY': 57,
    'SUBSCRIBER_DELETE': 58,
    'SUBSCRIBER_FORCAGE': 61,
}

PAYBOX_DIRECTPLUS_ENDPOINT = urlparse("https://preprod-ppps.paybox.com/PPPS.php")

class PayboxException(abstract_payment.PaymentException):
    
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return "PayboxError with code {code} and message \"{message}\"".format(**self.__dict__)


class PayboxManager(object):
    
    def __init__(self, ):
        pass

    def subscribe(self, member_id, card_number, expiration_date, cvv):
        """Subscribe new user to Paybox Direct Plus services"""
        response = self._request(
            TYPE=56, MONTANT=0, REFABONNE=member_id, PORTEUR=card_number, 
            DATEVAL=expiration_date, CVV=cvv
        )
        return response['PORTEUR'][0]

    def unsubscribe(self, member_id):
        response = self._request(
            TYPE=58, REFABONNE=member_id
        )

    def modify(self, member_id, card_number, expiration_date, cvv):
        response = self._request(
            TYPE=57, MONTANT=0, REFABONNE=member_id, PORTEUR=card_number, 
            DATEVAL=expiration_date, CVV=cvv
        )
        return response['PORTEUR'][0]

    def authorize_subscribed(self, member_id, card_number, expiration_date, cvv, amount):
        response = self._request(
            TYPE=51, MONTANT=amount, REFABONNE=member_id, PORTEUR=card_number,
            DATEVAL=expiration_date, CVV=cvv, 
            REFERENCE='6666'
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def authorize(self, card_number, expiration_date, cvv, amount):
        response = self._request(
            TYPE=1, MONTANT=amount, PORTEUR=card_number,
            DATEVAL=expiration_date, CVV=cvv, 
            REFERENCE='6666'
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]


    def debit_subscribed(self, member_id, amount, numappel, numtrans):
        response = self._request(
            TYPE=52, MONTANT=amount, REFABONNE=member_id,
            REFERENCE=random.randint(10**(LENGTH-1),10**LENGTH-1),
            NUMAPPEL=numappel, NUMTRANS=numtrans
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def debit(self, amount, numappel, numtrans):
        response = self._request(
            TYPE=2, MONTANT=amount,
            REFERENCE='6666',
            NUMAPPEL=numappel, NUMTRANS=numtrans
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def cancel_subscribed(self, member_id, card_number, expiration_date, cvv, numappel, numtrans):
        response = self._request(
            TYPE=55, MONTANT=100, REFABONNE=member_id, PORTEUR=card_number, DATEVAL=expiration_date, CVV=cvv,
            REFERENCE='6666',
            NUMAPPEL=numappel, NUMTRANS=numtrans
        )

    def cancel(self, numappel, numtrans, amount):
        print 'cancel'
        response = self._request(
            TYPE=5, MONTANT=amount, REFERENCE='6666', NUMAPPEL=str(numappel).rjust(10, '0'), NUMTRANS=str(numtrans).rjust(10, '0')
        )

    def credit(self, member_id, card_number, expiration_date, cvv, amount):
        response = self._request(
            TYPE=54, MONTANT=amount, REFABONNE=member_id, PORTEUR=card_number,
            DATEVAL=expiration_date, CVV=cvv,
            REFERENCE=random.randint(10**(LENGTH-1),10**LENGTH-1)
        )

    def verification(self, numappel, numtrans):
        print 'verify'
        response = self._request(
            TYPE=11, NUMAPPEL=numappel, NUMTRANS=numtrans, MONTANT=50,
        )

    def consultation(self, numappel, numtrans, amount):
        response = self._request(
            TYPE=17, NUMAPPEL=numappel, NUMTRANS=numtrans, MONTANT=50,
            REFERENCE='6666'
        )

    def _request(self, **kwargs):
        permanent_data['NUMQUESTION'] += 1
        data = permanent_data.copy()
        data.update(kwargs)
        print data
        data['DATEQ'] = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
        params = urllib.urlencode(data)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        with contextlib.closing(httplib.HTTPSConnection(PAYBOX_DIRECTPLUS_ENDPOINT.netloc, timeout=5)) as conn:
            conn.request("POST", PAYBOX_DIRECTPLUS_ENDPOINT.path, params, headers)
            response = conn.getresponse()
            #print filter(lambda ch: ord(ch) < 128, response.read())
            response = parse_qs(response.read())
            print response
            response_code = response['CODEREPONSE'][0]
            if int(response_code):
                raise PayboxException(response_code, response['COMMENTAIRE'][0])
            return response

# pm = PayboxManager()
# try:
#   p = pm.subscribe('dfgsd', '1111222233334444', '0114', '123')
#   print 'new user subscribed with partial number', p
# # print 'modify user', pm.modify('dfgsd', '1111222233334444', '0115', '123')
#   numquestion, numtrans = pm.authorize_subscribed('dfgsd', p, '0115', '123', 100)
#   #print 'authorize payment'
#   numquestion, numtrans = pm.debit_subscribed('dfgsd', 100, numquestion, numtrans)

#   # numquestion, numtrans = pm.authorize('1111222233334444', '0115', '123', 50)
#   # numquestion, numtrans = pm.debit(50, numquestion, numtrans)
#   #print 'make payment'
#   #print 'cancel payment', pm.cancel('dfgsd', p, '0115', '123', numquestion, numtrans)
#   #print 'credit', pm.credit('dfgsd', p, '0115', '123', 50)

# except PayboxException:
#   print pm.unsubscribe('dfgsd')
# else:
#   print pm.unsubscribe('dfgsd')

class PayboxDirectPayment(abstract_payment.AbstractPayment):

    def __init__(self):
        self.paybox_manager = PayboxManager()

    def preapproval(self, credit_card, cvv):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        try:
            self.numappel, self.numtrans = self.paybox_manager.authorize(
                credit_card.card_number, credit_card.expires, cvv, amount)
        except PayboxException:
            booking.state = booking.STATE.REJECTED
        else:
            booking.state = booking.STATE.AUTHORIZED
        finally:
            booking.save()

    def pay(self):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        self.paybox_manager.debit(amount, self.numappel, self.numtrans)
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def give_caution(self, amount, cancel_url, return_url):
        pass


class PayboxDirectPlusPayment(abstract_payment.AbstractPayment):

    def __init__(self):
        self.paybox_manager = PayboxManager()

    def preapproval(self, credit_card, cvv):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        try:
            self.numappel, self.numtrans = self.paybox_manager.authorize_subscribed(
                credit_card.holder.pk, credit_card.card_number, credit_card.expires, cvv, amount
            )
        except PayboxException:
            booking.state = booking.STATE.REJECTED
        else:
            booking.state = booking.STATE.AUTHORIZED
        finally:
            booking.save()
        
    def pay(self):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        self.paybox_manager.debit_subscribed(booking.borrower.pk, amount, self.numappel, self.numtrans)
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def give_caution(self, amount, cancel_url, return_url):
        pass

