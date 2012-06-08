from django.contrib.contenttypes.models import ContentType
from django.db import models

from eloue.rent.models import Booking
from eloue.payments import *
from eloue.accounts.models import CreditCard

class PaymentInformation(models.Model, abstract_payment.AbstractPayment):
    @property
    def booking(self):
        tipe = ContentType.objects.get_for_model(self)
        return Booking.objects.get(
            content_type__pk=tipe.id,
            object_id=self.id)

    class Meta:
        abstract = True

class NonPaymentInformation(PaymentInformation, non_payment.NonPayments):
	pass

class PaypalPaymentInformation(PaymentInformation, paypal_payment.AdaptivePapalPayments):
    preapproval_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    pay_key = models.CharField(null=True, editable=False, blank=True, max_length=255)

class PayboxPaymentInformation(PaymentInformation):
	numappel = models.CharField(max_length=20)
	numtrans = models.CharField(max_length=20)
	class Meta:
		abstract = True

class PayboxDirectPaymentInformation(PayboxPaymentInformation, paybox_payment.PayboxDirectPayment):
    numauth = models.CharField(max_length=20)

class PayboxDirectPlusPaymentInformation(PayboxPaymentInformation, paybox_payment.PayboxDirectPlusPayment):
    creditcard = models.ForeignKey(CreditCard, null=True)