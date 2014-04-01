from django.contrib.contenttypes.models import ContentType
from django.db import models

from eloue.rent.models import Booking
from eloue.payments import *
from eloue.accounts.models import CreditCard
from eloue.accounts.models import Patron

class PaymentInformation(models.Model, abstract_payment.AbstractPayment):
    # I did not used a generic reverse relation here, because of a bug in django 1.2
    # we must replace this with:
    # booking = generic.ReverseRelation(Booking)
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


class SlimPayMandateInformation(models.Model):
    RUM = models.CharField(null=True, blank=True, max_length=255)
    patron = models.ForeignKey(Patron)
    signatureDate = models.DateTimeField(null=True, blank=True)
    mandateFileName = models.CharField(null=True, blank=True, max_length=255)
    transactionId = models.CharField(null=True, blank=True, max_length=255)

