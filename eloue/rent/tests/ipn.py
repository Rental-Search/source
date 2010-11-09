# -*- coding: utf-8 -*-
import urllib

from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse

from eloue.rent.models import Booking


class TestPaypalIPN(TestCase):
    fixtures = ['patron', 'phones', 'address', 'price', 'product', 'booking']
    
    def test_preapproval_ipn(self):
        data = {
            'approved':'true',
            'charset':'windows-1252',
            'currency_code':'EUR',
            'current_number_of_payments':'0',
            'current_period_attempts':'0',
            'current_total_amount_of_all_payments':'0.0',
            'date_of_month':'0',
            'day_of_week':'NO_DAY_SPECIFIED',
            'ending_date':'2010-09-16T11:28:20.0-07:00',
            'max_number_of_payments':'null',
            'max_total_amount_of_all_payments':'112.6',
            'notify_version':'UNVERSIONED',
            'payment_period':'0',
            'pin_type':'NOT_REQUIRED',
            'preapproval_key':'PA-2NS525738W954192E',
            'sender_email':'eloue_1283761258_per@tryphon.org',
            'starting_date':'2010-09-13T11:28:20.0-07:00',
            'status':'ACTIVE',
            'test_ipn':'1',
            'transaction_type':'Adaptive Payment PREAPPROVAL',
            'verify_sign':'An5ns1Kso7MWUdW4ErQKJJJ4qi4-Av.UjqUcxQnthRSekpwrT2LmjDTm'
        }
        response = self.client.post(reverse('preapproval_ipn'), urllib.urlencode(data), content_type='application/x-www-form-urlencoded; charset=windows-1252;')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 2)
        self.assertTrue('alexandre.woog@e-loue.com' in mail.outbox[0].to)
        self.assertTrue('timothee.peignier@e-loue.com' in mail.outbox[1].to)
        booking = Booking.objects.get(preapproval_key="PA-2NS525738W954192E")
        self.assertEquals(booking.payment_state, Booking.PAYMENT_STATE.AUTHORIZED)
        self.assertEquals(booking.borrower.paypal_email, 'eloue_1283761258_per@tryphon.org')
    
    def test_pay_ipn(self):
        data = {
            'action_type':'PAY_PRIMARY',
            'cancel_url':'http://cancel.me',
            'charset':'windows-1252',
            'fees_payer':'PRIMARYRECEIVER',
            'ipn_notification_url':'http://www.postbin.org/1fi02go',
            'log_default_shipping_address_in_transaction':'false',
            'notify_version':'UNVERSIONED',
            'pay_key':'AP-1G646418FF723264N',
            'payment_request_date':'Mon Sep 13 02:31:12 PDT 2010',
            'return_url':'http://return.me',
            'reverse_all_parallel_payments_on_error':'false',
            'sender_email':'eloue_1283761258_per@tryphon.org',
            'status':'INCOMPLETE',
            'test_ipn':'1',
            'transaction[0].amount':'EUR 54.00',
            'transaction[0].id':'5G4772576R4998005',
            'transaction[0].id_for_sender_txn':'5UA91794R63363502',
            'transaction[0].is_primary_receiver':'true',
            'transaction[0].pending_reason':'NONE',
            'transaction[0].receiver':'sand_1266353156_biz@tryphon.org',
            'transaction[0].status':'Completed',
            'transaction[0].status_for_sender_txn':'Completed',
            'transaction[1].amount':'EUR 48.60',
            'transaction[1].is_primary_receiver':'false',
            'transaction[1].pending_reason':'NONE',
            'transaction[1].receiver':'eloue_1283761216_per@tryphon.org',
            'transaction_type':'Adaptive Payment PAY',
            'verify_sign':'ApZ7gM6YawE7YxcPuk9xgCNvybLAA.3oQL8gQFO3duXtJ-WfJ-dh1jJD'
        }
        response = self.client.post(reverse('pay_ipn'), urllib.urlencode(data), content_type='application/x-www-form-urlencoded; charset=windows-1252;')
        self.failUnlessEqual(response.status_code, 200)
        booking = Booking.objects.get(pay_key="AP-1G646418FF723264N")
        self.assertEquals(booking.payment_state, Booking.PAYMENT_STATE.HOLDED)
    
    
