# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal as D

from django.core.exceptions import ValidationError
from django.test import TestCase

from eloue.accounts.models import Patron
from eloue.rent.models import Booking, BorrowerComment, OwnerComment
from eloue.rent import models
from eloue.payments.paypal_payment import AdaptivePapalPayments
from mock import patch


class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return datetime.datetime(2010, 8, 15, 9, 0)

      
class BookingTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    def setUp(self):
        self.old_datetime = datetime.datetime
        datetime.datetime = MockDateTime
    
    def test_booking_created_at(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertEquals(booking.created_at, datetime.datetime.now())
    
    def test_start_and_end_date(self):
        booking = Booking(
            started_at=datetime.datetime.now() + datetime.timedelta(days=3),
            ended_at=datetime.datetime.now(),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_same_owner_and_borrower(self):
        booking = Booking(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=1,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_negative_total_amount(self):
        booking = Booking(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=-10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_pin_code(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertEqual(4, len(booking.pin))
        self.assertTrue(booking.pin.isdigit())
    
    def test_long_booking(self):
        booking = Booking(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=90),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=1
        )
        self.assertRaises(ValidationError, booking.full_clean)
    
    def test_insurance_price(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=80),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=4
        )
        self.assertEquals(booking.insurance_amount, D('0.500310'))
    
    def test_no_insurance(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=80),
            quantity=1,
            total_amount=10,
            state=4,
            owner_id=1,
            borrower_id=2,
            product_id=3
        )
        self.assertEquals(booking.insurance_amount, D(0))
        self.assertEquals(booking.product.payment_type, 1)
    
    def test_non_payment_preapproval(self):
        from eloue.payments.models import NonPaymentInformation
        payment = NonPaymentInformation.objects.create()
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.AUTHORIZING,
            owner_id=1,
            borrower_id=2,
            product_id=5,
            payment=payment
        )
        self.assertEquals(booking.product.payment_type, 0) #non payment 
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZING) 
        self.assertTrue(isinstance(booking.payment, NonPaymentInformation))
        booking.preapproval()
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZED) #state changed
    
    def test_non_payment_pay(self):
        from eloue.payments.models import NonPaymentInformation
        payment = NonPaymentInformation.objects.create()
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.ENDED,
            owner_id=1,
            borrower_id=2,
            product_id=5,
            payment=payment
        )
        self.assertEquals(booking.product.payment_type, 0) #non payment 
        self.assertEquals(booking.state, Booking.STATE.ENDED) 
        self.assertTrue(isinstance(booking.payment, NonPaymentInformation))
        booking.pay()
        self.assertEquals(booking.state, Booking.STATE.CLOSED) #state changed
    
    from eloue.payments.paybox_payment import PayboxManager
    @patch.object(PayboxManager, 'authorize_subscribed')
    def test_paybox_payment_preapproval(self, mock_authorize):
        from eloue.payments.models import PayboxDirectPlusPaymentInformation
        from eloue.accounts.models import CreditCard
        mock_authorize.return_value = '00012345', '000012345'
        creditcard = CreditCard.objects.create(
                expires='0119', card_number='1111222233334444', 
                holder=Patron.objects.get(pk=2)
            )
        payment = PayboxDirectPlusPaymentInformation.objects.create(
            creditcard=creditcard)
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.AUTHORIZING,
            owner_id=1,
            borrower_id=2,
            product_id=3,
            payment=payment
        )
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZING) 
        booking.preapproval(cvv='123')
        self.assertTrue(mock_authorize.called)
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZED)
        
    def tearDown(self):
        datetime.datetime = self.old_datetime
        
        
        
class CommentTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']
    def setUp(self):
        self.booking = Booking.objects.get(pk="1fac3d9f309c437b99f912bd08b09526")

    def test_comment_ok(self):
        borrower_comment = BorrowerComment(booking=self.booking, note=1, comment='bien')
        borrower_comment.save()
        self.assertEquals(borrower_comment.writer, self.booking.borrower)
        self.assertRaises(OwnerComment.DoesNotExist, lambda: borrower_comment.response)

        owner_comment = OwnerComment(booking=self.booking, note=2, comment='asd')
        owner_comment.save()
        self.assertEquals(owner_comment.writer, self.booking.owner)
        self.assertEquals(owner_comment.response, borrower_comment)
        self.assertEquals(borrower_comment.response, owner_comment)

        self.assertRaises(NotImplementedError, owner_comment.get_absolute_url)
    