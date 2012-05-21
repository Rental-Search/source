# -*- coding: utf-8 -*-
import httplib, urllib, urlparse, ssl, os
import datetime, random, contextlib, uuid
from decimal import Decimal as D

from backports.ssl_match_hostname import match_hostname
from django.conf import settings

import abstract_payment

TYPES = {
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

class PayboxException(abstract_payment.PaymentException):
    
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __unicode__(self):
        return u"PayboxError with code {code} and message \"{message}\"".format(**self.__dict__)


class HTTPSConnection(httplib.HTTPConnection):
    default_port = httplib.HTTPS_PORT
    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock = ssl.wrap_socket(self.sock, cert_reqs=ssl.CERT_REQUIRED, ca_certs=os.path.normpath(os.path.join(os.path.dirname(__file__), 'cacerts.txt')))
        match_hostname(self.sock.getpeercert(), self.host)


class PayboxManager(object):
    
    def __init__(self, ):
        self.PAYBOX_ENDPOINT = urlparse.urlparse(settings.PAYBOX_ENDPOINT)
        self.permanent_data = {
            'VERSION': settings.PAYBOX_VERSION,
            'SITE': settings.PAYBOX_SITE,
            'RANG': settings.PAYBOX_RANG,
            'CLE': settings.PAYBOX_CLE,
            'DEVISE': settings.PAYBOX_DEVISE,
            'ACTIVITE': settings.PAYBOX_ACTIVITE,
        }

    def _request(self, **kwargs):
        data = self.permanent_data.copy()
        data.update(kwargs)
        data['DATEQ'] = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
        data['NUMQUESTION'] = uuid.uuid4().fields[0]/2
        params = urllib.urlencode(data)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        with contextlib.closing(HTTPSConnection(self.PAYBOX_ENDPOINT.netloc, timeout=10)) as conn:
            conn.request("POST", self.PAYBOX_ENDPOINT.path, params, headers)
            response = conn.getresponse()
            response = urlparse.parse_qs(response.read())
            response_code = response['CODEREPONSE'][0]
            if int(response_code):
                raise PayboxException(response_code, response['COMMENTAIRE'][0].decode('latin1').encode('utf-8'))
            return response

    def subscribe(self, member_id, card_number, expiration_date, cvv):
        """Subscribe new user to Paybox Direct Plus services"""
        TYPE = TYPES['SUBSCRIBER_SUBSCRIBE']
        response = self._request(
            TYPE=TYPE, MONTANT=0, REFABONNE=member_id, PORTEUR=card_number, 
            DATEVAL=expiration_date, CVV=cvv
        )
        return response['PORTEUR'][0]

    def unsubscribe(self, member_id):
        TYPE = TYPES['SUBSCRIBER_DELETE']
        response = self._request(
            TYPE=TYPE, REFABONNE=member_id
        )

    def modify(self, member_id, card_number, expiration_date, cvv):
        TYPE = TYPES['SUBSCRIBER_MODIFY']
        response = self._request(
            TYPE=TYPE, MONTANT=0, REFABONNE=member_id, PORTEUR=card_number, 
            DATEVAL=expiration_date, CVV=cvv
        )
        return response['PORTEUR'][0]

    def authorize_subscribed(self, member_id, card_number, expiration_date, cvv, amount, reference):
        TYPE = TYPES['SUBSCRIBER_AUTHORIZE']
        response = self._request(
            TYPE=TYPE, MONTANT=amount, REFABONNE=member_id, PORTEUR=card_number,
            DATEVAL=expiration_date, CVV=cvv, 
            REFERENCE=reference
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def authorize(self, card_number, expiration_date, cvv, amount, reference):
        TYPE = TYPES['AUTHORIZE']
        response = self._request(
            TYPE=TYPE, MONTANT=amount, PORTEUR=card_number, 
            DATEVAL=expiration_date, CVV=cvv, REFERENCE=reference
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def debit_subscribed(self, member_id, amount, numappel, numtrans, reference):
        TYPE = TYPES['SUBSCRIBER_DEBIT']
        response = self._request(
            TYPE=TYPE, MONTANT=amount, REFABONNE=member_id,
            REFERENCE=reference, NUMAPPEL=numappel, NUMTRANS=numtrans
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def debit(self, amount, numappel, numtrans, reference):
        TYPE = TYPES['DEBIT']
        response = self._request(
            TYPE=TYPE, MONTANT=amount, REFERENCE=reference, NUMAPPEL=numappel, 
            NUMTRANS=numtrans
        )
        return response['NUMAPPEL'][0], response['NUMTRANS'][0]

    def cancel_subscribed(self, member_id, card_number, expiration_date, cvv, numappel, numtrans):
        TYPE = TYPES['SUBSCRIBER_CANCEL']
        raise NotImplementedError('we have to assign a proper reference number')
        response = self._request(
            TYPE=TYPE, MONTANT=100, REFABONNE=member_id, PORTEUR=card_number, DATEVAL=expiration_date, CVV=cvv,
            REFERENCE='6666',
            NUMAPPEL=numappel, NUMTRANS=numtrans
        )

    def cancel(self, numappel, numtrans, amount):
        TYPE = TYPES['CANCEL']
        raise NotImplementedError('we have to assign a proper reference number')
        response = self._request(
            TYPE=TYPE, MONTANT=amount, REFERENCE='6666', NUMAPPEL=numappel, NUMTRANS=numtrans
        )

    def credit(self, member_id, card_number, expiration_date, cvv, amount):
        TYPE = TYPES['SUBSCRIBER_CREDIT']
        raise NotImplementedError('we have to assign a proper reference number')
        response = self._request(
            TYPE=TYPE, MONTANT=amount, REFABONNE=member_id, PORTEUR=card_number,
            DATEVAL=expiration_date, CVV=cvv,
            REFERENCE='6666'
        )

    def verification(self, numappel, numtrans):
        raise NotImplementedError('TODO')
        TYPE = TYPES['']
        response = self._request(
            TYPE=TYPE, NUMAPPEL=numappel, NUMTRANS=numtrans, MONTANT=50,
        )

    def consultation(self, numappel, numtrans, amount):
        raise NotImplementedError('we have to assign a proper reference number')
        TYPE = TYPES['CONSULT']
        response = self._request(
            TYPE=TYPE, NUMAPPEL=numappel, NUMTRANS=numtrans, MONTANT=amount,
            REFERENCE='6666'
        )

class PayboxDirectPayment(abstract_payment.AbstractPayment):

    def __init__(self):
        raise NotImplementedError()
        self.paybox_manager = PayboxManager()

    def preapproval(self, credit_card, cvv):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        self.numappel, self.numtrans = self.paybox_manager.authorize(
            card_number=credit_card.card_number, expiration_date=credit_card.expires, 
            cvv=cvv, amount=amount, reference=booking.pk.hex
        )

    def pay(self, *args, **kwargs):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        self.paybox_manager.debit(
            amount=amount, numappel=self.numappel, numtrans=self.numtrans, 
            reference=booking.pk.hex
        )
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def give_caution(self, amount, cancel_url, return_url):
        pass


class PayboxDirectPlusPayment(abstract_payment.AbstractPayment):
    NOT_NEED_IPN = True

    def __init__(self):
        self.paybox_manager = PayboxManager()

    def preapproval(self, credit_card, cvv):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        self.numappel, self.numtrans = self.paybox_manager.authorize_subscribed(
            member_id=credit_card.holder.pk, card_number=credit_card.card_number, 
            expiration_date=credit_card.expires, cvv=cvv, amount=amount, 
            reference=booking.pk.hex
        )
        
    def pay(self, cancel_url, return_url):
        booking = self.booking
        amount = str(D(booking.total_amount*100).quantize(0))
        self.paybox_manager.debit_subscribed(
            member_id=booking.borrower.pk, amount=amount, numappel=self.numappel, 
            numtrans=self.numtrans, reference=booking.pk.hex
        )
        
    def execute_payment(self, *args, **kwargs):
        pass
        
    def cancel_preapproval(self, *args, **kwargs):
        pass
        
    def refund(self, *args, **kwargs):
        pass
        
    def give_caution(self, amount, cancel_url, return_url):
        pass


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