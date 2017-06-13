# -*- coding: utf-8 -*-
import datetime
import inspect
import calendar

from django.core.management.base import BaseCommand
from django.db.models import Max
from django.conf import settings
from django.core import mail

import logbook


class DjangoMailHandler(logbook.MailHandler):

    def deliver(self, msg, recipients):
        """Delivers the given message to a list of recpients."""
        mail.send_mail("billing error", msg.as_string(), self.from_addr, recipients)

handler = DjangoMailHandler(settings.SERVER_EMAIL, ['ops@e-loue.com'],
                              format_string=logbook.handlers.MAIL_FORMAT_STRING, level='INFO', bubble = True, record_delta=datetime.timedelta(seconds=0))

log = logbook.Logger('eloue.rent.sources')

def plus_one_month(date):
    import datetime, calendar
    month_days = calendar.monthrange(date.year, date.month)[1]
    return date + datetime.timedelta(days=month_days)

def minus_one_month(date):
    import datetime, calendar
    last_month = date.replace(day=1) - datetime.timedelta(days=1)
    month_days = calendar.monthrange(last_month.year, last_month.month)[1]
    return date - datetime.timedelta(days=month_days)

class Command(BaseCommand):
    help = ""
    args = ""

    def handle(self, *args, **options):
        from payments.models import PayboxDirectPlusPaymentInformation
        from accounts.models import Billing, Patron

        # generate new billings
        date_to = datetime.datetime.combine(datetime.date.today(), datetime.time())
        date_from = datetime.datetime.combine(minus_one_month(date_to), datetime.time())

        for patron in Patron.objects.filter(is_professional=True):
            if patron.next_billing_date() == date_from.date():
                try:
                    creditcard = patron.creditcard
                except CreditCard.DoesNotExist:
                    creditcard = None
                payment = PayboxDirectPlusPaymentInformation.objects.create(creditcard=creditcard)
                (billing, highlights, subscriptions, toppositions, phonenotifications, 
                    emailnotifications) = Billing.builder(patron, date_from, date_to)
                billing.payment = payment
                billing.save()

                from accounts.models import (BillingSubscription, 
                    BillingProductHighlight, BillingProductTopPosition, 
                    BillingPhoneNotification, BillingEmailNotification)

                for subscription in subscriptions:
                    BillingSubscription.objects.create(
                        billing=billing, subscription=subscription,
                        price=subscription.price(date_from, date_to))
                for highlight in highlights:
                    BillingProductHighlight.objects.create(
                        billing=billing, producthighlight=highlight, 
                        price=highlight.price(date_from, date_to))
                for topposition in toppositions:
                    BillingProductTopPosition.objects.create(
                        billing=billing, producttopposition=topposition,
                        price=topposition.price(date_from, date_to))
                for phonenotification in phonenotifications:
                    BillingPhoneNotification.objects.create(
                        billing=billing,  phonenotification=phonenotification,
                        price=phonenotification.price(date_from, date_to))
                for emailnotification in emailnotifications:
                    BillingEmailNotification.objects.create(
                        billing=billing, emailnotification=emailnotification,
                        price=emailnotification.price(date_from, date_to))

        # try to debit unpaid billings
        for billing in Billing.objects.select_related('billinghistory').filter(state='unpaid').annotate(last_try=Max('billinghistory__date')):
            if (billing.last_try is None) or (datetime.datetime.now() - billing.last_try) > datetime.timedelta(days=2):
                billing.pay()
            if billing.state == 'unpaid':
                with handler:
                    log.info(
                        'We were unable to charge the user {user}\'s credit card'
                        ' for the amount {total_amount}.'.format(
                            user=billing.patron.username, 
                            total_amount=billing.total_amount)
                        )


