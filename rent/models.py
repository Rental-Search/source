# -*- coding: utf-8 -*-
import datetime
import logbook
import types
import random
import urllib
import operator
from decimal import Decimal as D
from itertools import chain, groupby

from django_fsm import FSMField, transition
from django_fsm.signals import post_transition

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.formats import get_format
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from accounts.models import Patron
from products.models import Product
from products.choices import CURRENCY
from products.signals import post_save_to_update_product
from rent.choices import BOOKING_STATE, COMMENT_TYPE_CHOICES
from rent.decorators import incr_sequence
from rent.fields import UUIDField, IntegerAutoField
from rent.manager import BookingManager, CurrentSiteBookingManager, CommentManager
from payments.paypal_payment import AdaptivePapalPayments
from payments.non_payment import NonPayments

from eloue.signals import post_save_sites
from eloue.utils import create_alternative_email, itertools_accumulate


PAY_PROCESSORS = (NonPayments, AdaptivePapalPayments)

# FIXME: a regression has appeared that get_format() returns values for en-gb instead of fr-fr
DEFAULT_CURRENCY = get_format('CURRENCY', lang=settings.LANGUAGE_CODE) if not settings.CONVERT_XPF else "XPF"


USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

log = logbook.Logger('eloue.rent')



class Booking(models.Model):
    """A reservation"""
    uuid = UUIDField(primary_key=True)
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    quantity = models.IntegerField(default=1)

    state = FSMField(default=BOOKING_STATE.AUTHORIZING, choices=BOOKING_STATE, protected=True)
    
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

    # TODO: ownercomment and borrowercomment may be added automatically by a custom CommentForeignKey field
    # derived from forms.ForeignKey, by its contribute_to_related_class() method
    @property
    def ownercomment(self):
        return self.comments.get(type=COMMENT_TYPE_CHOICES.OWNER)

    @property
    def borrowercomment(self):
        return self.comments.get(type=COMMENT_TYPE_CHOICES.BORROWER)

    @property
    def _currency(self):
        if settings.CONVERT_XPF:
            return "EUR"
        else:
            return self.currency

    @staticmethod
    def _is_factory(state):
        def is_state(self):
            return self.state == getattr(BOOKING_STATE, state)
        return is_state

    @staticmethod
    def _max_rented_quantity(bookings):
        START = 1
        END = -1
        
        bookings_tuple = ((booking.started_at, booking.ended_at, booking.quantity) for booking in bookings)
        grouped_dates = groupby(sorted(chain.from_iterable(
          ((start, START, value), (end, END, value)) for start, end, value in bookings_tuple), 
          key=operator.itemgetter(0)), 
          key=operator.itemgetter(0)
        )
        sum_gen = (sum(map(lambda x: operator.mul(*operator.itemgetter(1, 2)(x)), j)) for i, j in grouped_dates)
        return max(itertools_accumulate(sum_gen, start=0))
    
    @staticmethod
    def calculate_available_quantity(product, started_at, ended_at):
        """Returns maximal available quantity between dates started_at and ended_at.
        """
        bookings = Booking.objects.filter(
            product=product
        ).filter(
            Q(state="pending")|Q(state="ongoing")
        ).filter(
            ~Q(ended_at__lte=started_at) & ~Q(started_at__gte=ended_at)
        )
        return product.quantity - Booking._max_rented_quantity(bookings)

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
    
    def send_incident_email(self, source, description):
        context = {'user': source.username, 'booking_id': self.pk, 'problem': description}
        message = create_alternative_email('rent/emails/incident', context, settings.DEFAULT_FROM_EMAIL, [source.email])
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
        >>> from products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.commission
        Decimal('2.0')
        """
        return self.total_amount * self.product.subtype.commission
        
    @property
    def total_commission(self):
        """ Return all the commission
        >>> from products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.total_commission
        Decimal('2.4590')
        """
        return self.commission + self.insurance_fee
    
    @property
    def net_price(self):
        """Return net price for owner
        >>> from products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.net_price
        Decimal('8.0')
        """
        return self.total_amount - self.commission
    
    @property
    def insurance_commission(self):
        """Return our commission on insurance
        >>> from products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.insurance_commission
        Decimal('0')
        """
        return self.total_amount * self.product.subtype.insurance_commission
    
    @property
    def insurance_fee(self):
        """Return insurance commission
        >>> from products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.insurance_fee
        Decimal('0.4590')
        """
        return self.total_amount * self.product.subtype.insurance_fee
    
    @property
    def insurance_taxes(self):
        """Return insurance taxes
        >>> from products.models import Product
        >>> booking = Booking(total_amount=10, product=Product())
        >>> booking.insurance_taxes
        Decimal('0.041310')
        """
        return self.insurance_fee * self.product.subtype.insurance_taxes
    
    # FSM conditions
    
    def not_need_ipn(self):
        return self.payment.NOT_NEED_IPN

    def is_expired(self):
        return self.started_at < datetime.datetime.now()

    # FSM actions
    
    @transition(field=state, source=BOOKING_STATE.AUTHORIZING, target=BOOKING_STATE.AUTHORIZED, conditions=[not_need_ipn])
    def preapproval(self, *args, **kwargs):
        self.payment.preapproval(self.pk, self.total_amount, self.currency, *args, **kwargs) # 'cvv'
        self.payment.save()
        self.send_ask_email()
    
    @transition(field=state, source=BOOKING_STATE.AUTHORIZED, target=BOOKING_STATE.REJECTED)
    def reject(self):
        self.send_rejection_email()
    
    @transition(field=state, source=[BOOKING_STATE.AUTHORIZING, BOOKING_STATE.AUTHORIZED], target=BOOKING_STATE.OUTDATED, conditions=[is_expired])
    def expire(self):
        pass
    
    @transition(field=state, source=BOOKING_STATE.AUTHORIZED, target=BOOKING_STATE.PENDING)
    def accept(self):
        self.payment.pay(self.pk, self.total_amount, self.currency)
        self.payment.save()
        self.send_acceptation_email()
        self.send_borrower_receipt()
    
    @transition(field=state, source=[BOOKING_STATE.AUTHORIZING, BOOKING_STATE.AUTHORIZED, BOOKING_STATE.PENDING], target=BOOKING_STATE.CANCELED)
    def cancel(self, *args, **kwargs):
        """Cancel preapproval for the borrower"""
        self.payment.cancel_preapproval()
        self.send_cancelation_email(*args, **kwargs) # 'source' = request.user
    
    @transition(field=state, source=BOOKING_STATE.PENDING, target=BOOKING_STATE.ONGOING)
    def activate(self):
        pass
    
    @transition(field=state, source=[BOOKING_STATE.ONGOING, BOOKING_STATE.ENDED, BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED], target=BOOKING_STATE.INCIDENT)
    def incident(self, *args, **kwargs):
        self.send_incident_email(*args, **kwargs)
    
    @transition(field=state, source=BOOKING_STATE.ONGOING, target=BOOKING_STATE.ENDED)
    def end(self):
        self.send_ended_email()
    
    @transition(field=state, source=BOOKING_STATE.ENDED, target=BOOKING_STATE.CLOSED)
    def close(self):
        """Return deposit_amount to borrower and pay the owner"""
        self.payment.execute_payment()
        self.send_owner_receipt()
        self.send_closed_email()
    
    @transition(field=state, source=BOOKING_STATE.PENDING)
    def contract(self):
        pass
    
    @transition(field=state, source=[BOOKING_STATE.AUTHORIZING, BOOKING_STATE.AUTHORIZED, BOOKING_STATE.REJECTED, BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED])
    def send_message(self):
        pass
    
    @transition(field=state, source=[BOOKING_STATE.ENDED, BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED])
    def leave_comment(self):
        pass
    
# FSM oosoleted actions
#
#     @transition(field=state, source=BOOKING_STATE.INCIDENT, target=BOOKING_STATE.DEPOSIT)
#     def litigation(self, amount=None, cancel_url='', return_url=''):
#         """Giving caution to owner"""
#         # FIXME : Deposit amount isn't considered in preapproval amount
#        
#         self.payment.give_caution(amount, cancel_url, return_url)
#     
#     @transition(field=state, source=BOOKING_STATE.INCIDENT, target=BOOKING_STATE.REFUNDED)
#     def refund(self):
#         """Refund borrower or owner if something as gone wrong"""
#         self.payment.refund()


class ProBooking(Booking):
    class Meta:
        proxy = True

    def send_ask_email(self):
        context = {'booking': self}
        message = create_alternative_email('rent/emails/owner_ask_pro', context, settings.DEFAULT_FROM_EMAIL, [self.owner.email])
        message.send()
        message = create_alternative_email('rent/emails/borrower_ask_pro', context, settings.DEFAULT_FROM_EMAIL, [self.borrower.email])
        message.send()

    # FSM actions

    @transition(field=Booking._meta.get_field('state'), source=BOOKING_STATE.PROFESSIONAL)
    def preapproval(self, *args, **kwargs):
        for phonenotification in self.owner.phonenotification_set.all():
            phonenotification.send('', self)
        for emailnotification in self.owner.emailnotification_set.all():
            emailnotification.send('', self)
        self.send_ask_email()

    @transition(field=Booking._meta.get_field('state'), source=BOOKING_STATE.PROFESSIONAL, target=BOOKING_STATE.PROFESSIONAL_SAW)
    def accept(self): # FIXME: rename to read
        pass


class BookingLog(models.Model):
    booking = models.ForeignKey(Booking)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    source_state = FSMField(choices=BOOKING_STATE)
    target_state = FSMField(choices=BOOKING_STATE)

    def __unicode__(self):
        return '{source_state} -> {target_state} @ {created_at}'.format(
            source_state=self.source_state, target_state=self.target_state, 
            created_at=self.created_at
        )

@receiver(post_transition, dispatch_uid='rent.models')
def state_logger(sender, instance, name, source, target, **kwargs):
    if isinstance(instance, Booking):
        BookingLog.objects.create(booking=instance, source_state=source, target_state=target)

class Comment(models.Model):
    booking = models.ForeignKey(Booking, related_name='comments')
    comment = models.TextField(_(u'Commentaire'))
    note = models.PositiveSmallIntegerField(_(u'Note'),
        choices=enumerate(xrange(6)),
        validators=[MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    type = models.PositiveSmallIntegerField(_(u'Type'),
        choices=COMMENT_TYPE_CHOICES,
        default=COMMENT_TYPE_CHOICES.OWNER,
        db_index=True
    )

    objects = models.Manager()
    ownercomments = CommentManager(COMMENT_TYPE_CHOICES.OWNER)
    borrowercomments = CommentManager(COMMENT_TYPE_CHOICES.BORROWER)

    @property
    def author(self):
        return self.booking.owner if type == COMMENT_TYPE_CHOICES.OWNER else self.booking.borrower

    @property
    def response(self):
        raise self.booking.borrowercomment if type == COMMENT_TYPE_CHOICES.OWNER else self.booking.ownercomment

    @property
    def writer(self):
        raise self.booking.owner if type == COMMENT_TYPE_CHOICES.OWNER else self.booking.borrower

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
        ordering = ['-created_at']
    
class OwnerComment(Comment):
    objects = CommentManager(COMMENT_TYPE_CHOICES.OWNER)

    class Meta:
        proxy = True

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
    objects = CommentManager(COMMENT_TYPE_CHOICES.BORROWER)

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = COMMENT_TYPE_CHOICES.BORROWER
        super(BorrowerComment, self).__init__(*args, **kwargs)

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

    def __unicide__(self):
        return self.uuid
    
    @incr_sequence('sinister_id', 'rent_sinister_sinister_id_seq')
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Sinister, self).save(*args, **kwargs)
    

post_save.connect(post_save_sites, sender=Booking)
post_save.connect(post_save_sites, sender=ProBooking)
post_save.connect(post_save_to_update_product, sender=BorrowerComment)
post_save.connect(post_save_to_update_product, sender=OwnerComment)

