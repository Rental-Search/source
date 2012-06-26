# -*- coding: utf-8 -*-
import datetime
import logbook
import types
import random
import urllib

from decimal import Decimal as D, ROUND_CEILING, ROUND_FLOOR
from fsm.fields import FSMField
from fsm import transition
from pyke import knowledge_engine
from urlparse import urljoin
from datetime import timedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.utils.formats import get_format
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.core.urlresolvers import reverse

from eloue.accounts.models import Patron
from eloue.products.models import CURRENCY, UNIT, Product, PAYMENT_TYPE
from eloue.products.utils import Enum
from eloue.products.signals import post_save_to_update_product
from eloue.rent.decorators import incr_sequence
from eloue.rent.fields import UUIDField, IntegerAutoField
from eloue.rent.manager import BookingManager, CurrentSiteBookingManager
from eloue.payments.paypal_payment import AdaptivePapalPayments, PaypalError
from eloue.payments.non_payment import NonPayments
from eloue.payments.fsm_transition import smart_transition
from eloue.signals import post_save_sites
from eloue.utils import create_alternative_email, convert_from_xpf


PAY_PROCESSORS = (NonPayments, AdaptivePapalPayments)

BOOKING_STATE = Enum([
    ('authorizing', 'AUTHORIZING', _(u"En cours d'autorisation")),
    ('authorized', 'AUTHORIZED', _(u"En attente")),
    ('rejected', 'REJECTED', _(u'Rejeté')),
    ('canceled', 'CANCELED', _(u'Annulé')),
    ('pending', 'PENDING', _(u'A venir')),
    ('ongoing', 'ONGOING', _(u'En cours')),
    ('ended', 'ENDED', _(u'Terminé')),
    ('incident', 'INCIDENT', _(u'Incident')),
    ('refunded', 'REFUNDED', _(u'Remboursé')),
    ('deposit', 'DEPOSIT', _(u'Caution versée')),
    ('closing', 'CLOSING', _(u"En attende de clôture")),
    ('closed', 'CLOSED', _(u'Clôturé')),
    ('outdated', 'OUTDATED', _(u"Dépassé")),
    ('unaccepted', 'UNACCEPTED', _(u"Pas accepté")),
    ('accepted_unauthorized', 'ACCEPTED_UNAUTHORIZED', _(u"Accepté et en cours d'autorisation"))
])

DEFAULT_CURRENCY = get_format('CURRENCY') if not settings.CONVERT_XPF else "XPF"


USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

PACKAGES_UNIT = {
    'hour': UNIT.HOUR,
    'week_end': UNIT.WEEK_END,
    'day': UNIT.DAY,
    'week': UNIT.WEEK,
    'two_weeks': UNIT.TWO_WEEKS,
    'month': UNIT.MONTH
}

PACKAGES = {
    UNIT.HOUR: lambda amount, delta, round=True: amount * (delta.seconds / D('3600')),
    UNIT.WEEK_END: lambda amount, delta, round=True: amount,
    UNIT.DAY: lambda amount, delta, round=True: amount * (max(delta.days + delta.seconds / D('86400'), 1) if round else delta.days + delta.seconds / D('86400')),
    UNIT.WEEK: lambda amount, delta, round=True: amount * (delta.days + delta.seconds / D('86400')),
    UNIT.TWO_WEEKS: lambda amount, delta, round=True: amount * (delta.days + delta.seconds / D('86400')),
    UNIT.MONTH: lambda amount, delta, round=True: amount * (delta.days + delta.seconds / D('86400')),
}

log = logbook.Logger('eloue.rent')


class Booking(models.Model):
    """A reservation"""
    uuid = UUIDField(primary_key=True)
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    quantity = models.IntegerField(default=1)

    state = FSMField(default='authorizing', choices=BOOKING_STATE)
    
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=DEFAULT_CURRENCY)
    
    owner = models.ForeignKey(Patron, related_name='bookings')
    borrower = models.ForeignKey(Patron, related_name='rentals')
    product = models.ForeignKey(Product, related_name='bookings')
    

    contract_id = IntegerAutoField(unique=True, db_index=True)
    pin = models.CharField(blank=True, max_length=4)
    ip = models.IPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(blank=True, editable=False)
    canceled_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    preapproval_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    pay_key = models.CharField(null=True, editable=False, blank=True, max_length=255)
    
    sites = models.ManyToManyField(Site, related_name='bookings')
    
    on_site = CurrentSiteBookingManager()
    objects = BookingManager()

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    payment = generic.GenericForeignKey('content_type', 'object_id')

    STATE = BOOKING_STATE
    
    @incr_sequence('contract_id', 'rent_booking_contract_id_seq')
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
            self.pin = str(random.randint(1000, 9999))
            self.deposit_amount = self.product.deposit_amount
            if self.product.has_insurance:
                self.insurance_amount = self.insurance_fee + self.insurance_taxes + self.insurance_commission
            else:
                self.insurance_amount = D(0)
        super(Booking, self).save(*args, **kwargs)
        
    @permalink
    def get_absolute_url(self):
        return ('booking_detail', [self.pk.hex])
    
    def __unicode__(self):
        return self.product.summary
    
    def __init__(self, *args, **kwargs):
        super(Booking, self).__init__(*args, **kwargs)
        for state in BOOKING_STATE.enum_dict:
            setattr(self, "is_%s" % state.lower(), types.MethodType(self._is_factory(state), self))
    
    @staticmethod
    def _is_factory(state):
        def is_state(self):
            return self.state == getattr(BOOKING_STATE, state)
        return is_state
    
    @staticmethod
    def calculate_available_quantity(product, started_at, ended_at):
        """Returns maximal available quantity between dates started_at and ended_at.
        """
        from itertools import groupby, chain, izip
        from datetime import datetime
        import operator
        from operator import itemgetter, mul, add

        def max_rented_quantity(bookings):
            
            def _accumulate(iterable, func=operator.add, start=None):
                """
                Modified version of Python 3.2's itertools.accumulate.
                """
                # accumulate([1,2,3,4,5]) --> 0 1 3 6 10 15
                # accumulate([1,2,3,4,5], operator.mul) --> 0 1 2 6 24 120
                yield 0
                it = iter(iterable)
                total = next(it)
                yield total
                for element in it:
                    total = func(total, element)
                    yield total
                yield
            
            START = 1
            END = -1
            
            bookings_tuple = ((booking.started_at, booking.ended_at, booking.quantity) for booking in bookings)
            grouped_dates = groupby(sorted(chain.from_iterable(
              ((start, START, value), (end, END, value)) for start, end, value in bookings_tuple), 
              key=itemgetter(0)), 
              key=itemgetter(0)
            )
            return max(_accumulate(sum(map(lambda x: mul(*itemgetter(1, 2)(x)), j)) for i, j in grouped_dates))
        
        bookings = Booking.objects.filter(
            product=product
        ).filter(
            Q(state="pending")|Q(state="ongoing")
        ).filter(
            ~Q(ended_at__lte=started_at) & ~Q(started_at__gte=ended_at)
        )
        return product.quantity - max_rented_quantity(bookings)

    @staticmethod
    def calculate_price(product, started_at, ended_at):
        delta = ended_at - started_at
        
        engine = knowledge_engine.engine((__file__, '.rules'))
        engine.activate('pricing')
        for price in product.prices.all():
            engine.assert_('prices', 'price', (price.unit, price.day_amount))
        vals, plans = engine.prove_1_goal('pricing.pricing($type, $started_at, $ended_at, $delta)', started_at=started_at, ended_at=ended_at, delta=delta)
        engine.reset()

        amount, unit = D(0), PACKAGES_UNIT[vals['type']]
        package = PACKAGES[unit]
        
        for price in product.prices.filter(unit=unit, started_at__isnull=False, ended_at__isnull=False):
            price_delta = price.delta(started_at, ended_at)
            delta -= price_delta
            amount += package(price.day_amount, price_delta, False)
        
        if (delta.days > 0 or delta.seconds > 0):
            price = product.prices.get(unit=unit, started_at__isnull=True, ended_at__isnull=True)
            null_delta = timedelta(days=0)
            amount += package(price.day_amount, null_delta if null_delta > delta else delta)
        
        return unit, amount.quantize(D(".00"))

    def send_recovery_email(self):
        context = {
            'booking': self,
            'preapproval_url': settings.PAYPAL_COMMAND % urllib.urlencode({
                'cmd': '_ap-preapproval',
                'preapprovalkey': self.preapproval_key
            })
        }
        message = create_alternative_email('rent/emails/borrower_recovery', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    def send_ask_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_ask', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_ask', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    def send_acceptation_email(self):
        context = {'booking': self}
        if not self.owner.is_professional:
            contract = self.product.subtype.contract_generator(self)
            print contract
            content = contract.getvalue()
        message = create_alternative_email('rent/emails/owner_acceptation', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        if not self.owner.is_professional: 
            message.attach('contrat.pdf', content, 'application/pdf')
        message.send()
        message = create_alternative_email('rent/emails/borrower_acceptation', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        if not self.owner.is_professional:    
            message.attach('contrat.pdf', content, 'application/pdf')
        message.send()
    
    def send_borrower_receipt(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/borrower_receipt', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()

    def send_owner_receipt(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_receipt', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()

    def send_rejection_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/borrower_rejection', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    def send_cancelation_email(self, source=None):
        context = {'booking': self}
        if self.owner == source:
            message = create_alternative_email('rent/emails/owner_cancelation_to_owner', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
            message.send()
            message = create_alternative_email('rent/emails/owner_cancelation_to_borrower', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
            message.send()
        else:
            message = create_alternative_email('rent/emails/borrower_cancelation_to_owner', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
            message.send()
            message = create_alternative_email('rent/emails/borrower_cancelation_to_borrower', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
            message.send()
    
    def send_ended_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_ended', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_ended', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    
    def send_closed_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_closed', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_closed', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()
    
    @property
    def commission(self):
        """Return our commission
        >>> from eloue.products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.commission
        Decimal('2.0')
        """
        return self.total_amount * self.product.subtype.commission
        
    @property
    def total_commission(self):
        """ Return all the commission
        >>> from eloue.products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.total_commission
        Decimal('2.6470')
        """
        return self.commission + self.insurance_fee
    
    @property
    def net_price(self):
        """Return net price for owner
        >>> from eloue.products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.net_price
        Decimal('8.0')
        """
        return self.total_amount - self.commission
    
    @property
    def insurance_commission(self):
        """Return our commission on insurance
        >>> from eloue.products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.insurance_commission
        Decimal('0')
        """
        return self.total_amount * self.product.subtype.insurance_commission
    
    @property
    def insurance_fee(self):
        """Return insurance commission
        >>> from eloue.products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.insurance_fee
        Decimal('0.6470')
        """
        return self.total_amount * self.product.subtype.insurance_fee
    
    @property
    def insurance_taxes(self):
        """Return insurance taxes
        >>> from eloue.products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.insurance_taxes
        Decimal('0.058230')
        """
        return self.insurance_fee * self.product.subtype.insurance_taxes
    
    def not_need_ipn(self):
        return self.payment.NOT_NEED_IPN
        
    @smart_transition(source='authorizing', target='authorized', conditions=[not_need_ipn], save=True)
    def preapproval(self, *args, **kwargs):
        self.payment.preapproval(*args, **kwargs)
        self.payment.save()
        self.send_ask_email()
        
    @transition(source='authorized', target='pending', save=True)
    def accept(self):
        domain = Site.objects.get_current().domain
        protocol = "https"
        cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[self.pk.hex]))
        return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[self.pk.hex]))

        self.payment.pay(cancel_url, return_url)
        self.payment.save()
        self.send_acceptation_email()
        self.send_borrower_receipt()

    @transition(source='pending', target='ongoing', save=True)
    def activate(self):
        pass

    @transition(source='ongoing', target='ended', save=True)
    def end(self):
        self.send_ended_email()
    
    @transition(source='ended', target='closing', save=True)
    @smart_transition(source='closing', target='closed', conditions=[not_need_ipn], save=True)
    def pay(self):
        """Return deposit_amount to borrower and pay the owner"""
        self.payment.execute_payment()
        self.send_owner_receipt()
    
    @transition(source=['authorized', 'pending'], target='canceled', save=True)
    def cancel(self):
        """Cancel preapproval for the borrower"""
        self.payment.cancel_preapproval()
    
    @transition(source='incident', target='deposit', save=True)
    def litigation(self, amount=None, cancel_url='', return_url=''):
        """Giving caution to owner"""
        # FIXME : Deposit amount isn't considered in preapproval amount
       
        self.payment.give_caution(amount, cancel_url, return_url)
    
    @transition(source='incident', target='refunded', save=True)
    def refund(self):
        """Refund borrower or owner if something as gone wrong"""
        self.payment.refund()
    
    @property
    def _currency(self):
        if settings.CONVERT_XPF:
            return "EUR"
        else:
            return self.currency

class Comment(models.Model):
    booking = models.OneToOneField(Booking)
    comment = models.TextField(_(u'Commentaire'))
    note = models.PositiveSmallIntegerField(_(u'Note'),
        choices=enumerate(xrange(6)),
        validators=[MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(editable=False, auto_now_add=True)

    @property
    def response(self):
        raise NotImplementedError
    
    @property
    def writer(self):
        raise NotImplementedError

    #@permalink
    def get_absolute_url(self):
        raise NotImplementedError
        #return ('booking_detail', [self.pk.hex])

    @property
    def product(self):
        return self.booking.product

    def __unicode__(self):
        return self.comment

    class Meta:
        abstract = True
        ordering = ['-created_at']
    
class OwnerComment(Comment):
    @property
    def response(self):
        return self.booking.borrowercomment
    @property
    def writer(self):
        return self.booking.owner

    def send_notification_comment_email(self):
        context = {'comment': self, 'author': self.booking.owner, 'patron': self.booking.borrower}
        message = create_alternative_email('rent/emails/comment', context, settings.DEFAULT_FROM_EMAIL, [self.booking.borrower.email])
        message.send()
    
class BorrowerComment(Comment):
    @property
    def response(self):
        return self.booking.ownercomment
    @property
    def writer(self):
        return self.booking.borrower

    def send_notification_comment_email(self):
        context = {'comment': self, 'author': self.booking.borrower, 'patron': self.booking.owner}
        message = create_alternative_email('rent/emails/comment', context, settings.DEFAULT_FROM_EMAIL, [self.booking.owner.email])
        message.send()
    
class Sinister(models.Model):
    uuid = UUIDField(primary_key=True)
    sinister_id = IntegerAutoField(unique=True, db_index=True)
    description = models.TextField()
    patron = models.ForeignKey(Patron, related_name='sinisters')
    booking = models.ForeignKey(Booking, related_name='sinisters')
    product = models.ForeignKey(Product, related_name='sinisters')
    
    created_at = models.DateTimeField(blank=True, editable=False)
    
    @incr_sequence('sinister_id', 'rent_sinister_sinister_id_seq')
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Sinister, self).save(*args, **kwargs)
    

post_save.connect(post_save_sites, sender=Booking)
post_save.connect(post_save_to_update_product, sender=BorrowerComment)
post_save.connect(post_save_to_update_product, sender=OwnerComment)

