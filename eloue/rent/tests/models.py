# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal as D

from django.core.exceptions import ValidationError
from django.test import TestCase

from eloue.rent.models import Booking
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
        self.assertEquals(booking.insurance_amount, D('0.58860'))
    
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
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.AUTHORIZING,
            owner_id=1,
            borrower_id=2,
            product_id=5
        )
        self.assertEquals(booking.product.payment_type, 0) #non payment 
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZING) 
        booking.init_payment_processor() 
        self.assertTrue(isinstance(booking.payment_processor, models.PAY_PROCESSORS[0]))
        booking.preapproval()
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZED) #state changed
    
    def test_non_payment_pay(self):
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.ENDED,
            owner_id=1,
            borrower_id=2,
            product_id=5
        )
        self.assertEquals(booking.product.payment_type, 0) #non payment 
        self.assertEquals(booking.state, Booking.STATE.ENDED) 
        booking.init_payment_processor()
        self.assertTrue(isinstance(booking.payment_processor, models.PAY_PROCESSORS[0]))
        booking.pay()
        self.assertEquals(booking.state, Booking.STATE.CLOSED) #state changed
    
    @patch.object(AdaptivePapalPayments, 'preapproval')
    def test_paypal_payment_preapproval(self, mock_preapproval):
        mock_preapproval.return_value = 'PA-7BT08456PP218331A'
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.AUTHORIZING,
            owner_id=1,
            borrower_id=2,
            product_id=3
        )
        self.assertEquals(booking.product.payment_type, 1) #paypal payment 
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZING) 
        booking.init_payment_processor() 
        self.assertTrue(isinstance(booking.payment_processor, models.PAY_PROCESSORS[1]))
        booking.preapproval()
        self.assertTrue(mock_preapproval.called)
        self.assertEquals(booking.state, Booking.STATE.AUTHORIZING) # make sure that state didn't changed
    
    @patch.object(AdaptivePapalPayments, 'execute_payment')
    def test_paypal_payment_pay(self, mock_execute_payment):
        mock_execute_payment.return_value = None
        booking = Booking.objects.create(
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now() + datetime.timedelta(days=3),
            quantity=1,
            total_amount=10,
            state=Booking.STATE.ENDED,
            owner_id=1,
            borrower_id=2,
            product_id=3
        )
        self.assertEquals(booking.product.payment_type, 1) #paypal payment  
        self.assertEquals(booking.state, Booking.STATE.ENDED) 
        booking.init_payment_processor()
        self.assertTrue(isinstance(booking.payment_processor, models.PAY_PROCESSORS[1]))
        booking.pay()
        self.assertTrue(mock_execute_payment.called)
        self.assertEquals(booking.state, Booking.STATE.CLOSING) #make sure that state change once
        
    def tearDown(self):
        datetime.datetime = self.old_datetime

        
        
        
        
        
    
