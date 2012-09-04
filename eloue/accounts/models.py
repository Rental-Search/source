# -*- coding: utf-8 -*-
import datetime
import logbook
import uuid
import urllib2
import calendar
from decimal import Decimal as D

import simplejson
import facebook

from imagekit.models import ImageSpec
from imagekit.processors import resize, Adjust, Transpose

from fsm.fields import FSMField
from fsm import transition

from django.core.exceptions import ValidationError
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db.models import permalink, Q, signals, Count, Sum
from django.utils.encoding import smart_unicode
from django.utils.formats import get_format
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.defaultfilters import slugify

from eloue.accounts.manager import PatronManager
from eloue.geocoder import GoogleGeocoder
from eloue.products.utils import Enum
from eloue.products.signals import post_save_to_batch_update_product
from eloue.signals import post_save_sites, pre_delete_creditcard
from eloue.utils import create_alternative_email, cache_to
from eloue.payments.paypal_payment import accounts, PaypalError
from eloue.payments import paypal_payment

CIVILITY_CHOICES = Enum([
    (0, 'MME', _('Madame')),
    (1, 'MLLE', _('Mademoiselle')),
    (2, 'M', _('Monsieur'))
])

COUNTRY_CHOICES = Enum([
    ('FR', 'FR', _(u'France')),
    ('BE', 'BE', _(u'Belgique')),
    ('LU', 'LU', _(u'Luxembourg')),
    ('RE', 'RE', _(u'Réunion')),
    ('DE', 'DE', _(u'Allemagne')),
    ('AD', 'AD', _(u'Andore')),
    ('AT', 'AT', _(u'Autriche')),
    ('CA', 'CA', _(u'Canada')),
    ('CY', 'CY', _(u'Chypre')),
    ('DK', 'DK', _(u'Danemark')),
    ('ES', 'ES', _(u'Espagne')),
    ('US', 'US', _(u'États-Unis')),
    ('FI', 'FI', _(u'Finlande')),
    ('GR', 'GR', _(u'Grèce')),
    ('GP', 'GP', _(u'Guadeloupe')),
    ('GG', 'GG', _(u'Guernesey')),
    ('GF', 'GF', _(u'Guyane Française')),
    ('HU', 'HU', _(u'Hongrie')),
    ('IE', 'IE', _(u'Irlande')),
    ('IS', 'IS', _(u'Islande')),
    ('IT', 'IT', _(u'Italie')),
    ('JP', 'JP', _(u'Japon')),
    ('JE', 'JE', _(u'Jersey')),
    ('LV', 'LV', _(u'Lettonie')),
    ('LI', 'LI', _(u'Liechtenstein')),
    ('LT', 'LT', _(u'Lituanie')),
    ('MT', 'MT', _(u'Malte')),
    ('MQ', 'MQ', _(u'Martinique')),
    ('MU', 'MU', _(u'Maurice')),
    ('YT', 'YT', _(u'Mayotte')),
    ('MC', 'MC', _(u'Monaco')),
    ('MA', 'MA', _(u'Maroc')),
    ('NO', 'NO', _(u'Norvège')),
    ('NC', 'NC', _(u'Nouvelle-Calédonie')),
    ('NL', 'NL', _(u'Pays-Bas')),
    ('PL', 'PL', _(u'Pologne')),
    ('PF', 'PF', _(u'Polynésie Française')),
    ('PT', 'PT', _(u'Portugal')),
    ('RO', 'RO', _(u'Roumanie')),
    ('GB', 'GB', _(u'Royaume-Uni')),
    ('RU', 'RU', _(u'Russie, Fédération de')),
    ('PM', 'PM', _(u'Saint-Pierre-et-Miquelon')),
    ('VA', 'VA', _(u'Saint-Siège (État de la cité du Vatican)')),
    ('SE', 'SE', _(u'Suède')),
    ('CH', 'CH', _(u'Suisse')),
    ('CZ', 'CZ', _(u'Tchèque, République')),
    ('TF', 'TF', _(u'Terres Australes Françaises')),
    ('TN', 'TN', _(u'Tunisie')),
    ('TR', 'TR', _(u'Turquie'))
])

PHONE_TYPES = Enum([
    (0, 'HOME', _('Domicile')),
    (1, 'WORK', _('Travail')),
    (2, 'MOBILE', _('Mobile')),
    (3, 'FAX', _('Fax')),
    (4, 'OTHER', _('Autre'))
])

DEFAULT_CURRENCY = get_format('CURRENCY')

log = logbook.Logger('eloue.accounts')

def upload_to(instance, filename):
    return 'pictures/avatars/%s.jpg' % uuid.uuid4().hex

class Avatar(models.Model):

    patron = models.OneToOneField(User, related_name='avatar_old')
    image = models.ImageField(upload_to=upload_to)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)

    thumbnail = ImageSpec(
        processors=[
            resize.Crop(width=60, height=60), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=True, cache_to=cache_to
    )
    profil = ImageSpec(
        processors=[
            resize.Fit(width=100), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=True, cache_to=cache_to
    )
    display = ImageSpec(
        processors=[
            resize.Fit(width=180), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=True, cache_to=cache_to
    )
    
    product_page = ImageSpec(
        processors=[
            resize.Fit(width=74, height=74), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=True, cache_to=cache_to
    )
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Avatar, self).delete(*args, **kwargs)

class Language(models.Model):

    lang = models.CharField(max_length=30)

    def __unicode__(self):
        return ugettext(self.lang)
    
class Patron(User):
    """A member"""
    civility = models.PositiveSmallIntegerField(_(u"Civilité"), null=True, blank=True, choices=CIVILITY_CHOICES)
    company_name = models.CharField(null=True, blank=True, max_length=255)
    subscriptions = models.ManyToManyField('ProPackage', through='Subscription')

    activation_key = models.CharField(null=True, blank=True, max_length=40)
    is_subscribed = models.BooleanField(_(u'newsletter'), default=False, help_text=_(u"Précise si l'utilisateur est abonné à la newsletter"))
    new_messages_alerted = models.BooleanField(_(u'alerts if new messages come'), default=True, help_text=_(u"Précise si l'utilisateur est informé par email s'il a nouveaux messages"))
    is_professional = models.NullBooleanField(_('professionnel'), blank=True, default=None, help_text=_(u"Précise si l'utilisateur est un professionnel"))
    modified_at = models.DateTimeField(_('date de modification'), editable=False, auto_now=True)
    affiliate = models.CharField(null=True, blank=True, max_length=10)
    slug = models.SlugField(unique=True, db_index=True)
    paypal_email = models.EmailField(null=True, blank=True)
    sites = models.ManyToManyField(Site, related_name='patrons')
    
    avatar = models.ImageField(upload_to=upload_to, null=True, blank=True)

    default_address = models.ForeignKey('Address', null=True, blank=True, related_name="+")
    default_number = models.ForeignKey('PhoneNumber', null=True, blank=True, related_name="+")

    customers = models.ManyToManyField('self', symmetrical=False)

    about = models.TextField(blank=True, null=True)
    work = models.CharField(max_length=75, blank=True, null=True)
    school = models.CharField(max_length=75, blank=True, null=True)
    hobby = models.CharField(max_length=75, blank=True, null=True)
    languages = models.ManyToManyField(Language, blank=True, null=True)

    drivers_license_date = models.DateTimeField(_(u"Date d'obtention"), blank=True, null=True)
    drivers_license_number = models.CharField(_(u"Numéro du permis"), blank=True, max_length=32)

    date_of_birth = models.DateTimeField(_(u"Date de naissance"), blank=True, null=True)
    place_of_birth = models.CharField(_(u"Lieu de naissance"), blank=True, max_length=255)

    on_site = CurrentSiteManager()
    objects = PatronManager()

    rib = models.CharField(max_length=23, blank=True)

    url = models.URLField(_(u"Site internet"), blank=True, help_text=_(u"L'affichage de l'adresse du site est facturée 5€ par mois."))

    thumbnail = ImageSpec(
        processors=[
            resize.Crop(width=60, height=60), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='avatar', pre_cache=True, cache_to=cache_to
    )
    profil = ImageSpec(
        processors=[
            resize.Fit(width=100), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='avatar', pre_cache=True, cache_to=cache_to
    )
    display = ImageSpec(
        processors=[
            resize.Fit(width=180), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='avatar', pre_cache=True, cache_to=cache_to
    )
    
    product_page = ImageSpec(
        processors=[
            resize.Fit(width=74, height=74), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='avatar', pre_cache=True, cache_to=cache_to
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.is_professional:
                self.slug = slugify(self.company_name)
            else:
                self.slug = slugify(self.username)
        super(Patron, self).save(*args, **kwargs)

    def __eq__(self, other):
        """
        To resolve the user comparing problems in other projet lib.
        """
        if isinstance(other, User):
            if other.pk == self.pk:
                return True

    @permalink
    def get_absolute_url(self):
        return ('patron_detail', [self.slug])

    def clean(self):
        if self.pk:  # TODO : Might need some improvements and more tests
            if Patron.objects.exclude(pk=self.pk).filter(email=self.email).exists():
                raise ValidationError(_(u"Un utilisateur utilisant cet email existe déjà"))
            if Patron.objects.exclude(pk=self.pk).filter(username=self.username).exists():
                raise ValidationError(_(u"Un utilisateur utilisant ce nom d'utilisateur existe déjà"))
        else:
            if Patron.objects.exists(email=self.email):
                raise ValidationError(_(u"Un utilisateur utilisant cet email existe déjà"))
            if Patron.objects.exists(username=self.username):
                raise ValidationError(_(u"Un utilisateur utilisant ce nom d'utilisateur existe déjà"))

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def has_paypal(self):
        """Indicates if user has an "verified" paypal account
        >>> patron = Patron(paypal_email=None)
        >>> patron.has_paypal()
        False
        >>> patron = Patron(paypal_email="elmo@paypal.com")
        >>> patron.has_paypal()
        True
        >>> patron = Patron(paypal_email="")
        >>> patron.has_paypal()
        False
        """
        from django.core.validators import validate_email
        try:
            validate_email(self.paypal_email)
            return True
        except ValidationError:
            return False

    def create_account(self, return_url=None):
        try:
            address = self.addresses.all()[0]
            response = accounts.create_account(
                accountType='Premier',
                address={
                    'line1': address.address1,
                    'city': address.city,
                    'postalCode': address.zipcode,
                    'countryCode': address.country if address.country != COUNTRY_CHOICES.NC else COUNTRY_CHOICES.FR
                },
                emailAddress=self.paypal_email,
                name={
                    'firstName': self.first_name,
                    'lastName': self.last_name
                },
                registrationType="Web",
                citizenshipCountryCode=address.country,
                preferredLanguageCode='fr_FR',
                contactPhoneNumber=self.phones.all()[0].number,
                currencyCode=DEFAULT_CURRENCY,
                createAccountWebOptions={
                    'returnUrl': return_url,
                    'returnUrlDescription': ugettext(u"e-loue"),
                    'showAddCreditCard': False
                },
                suppressWelcomeEmail=True,
            )
            return response['redirectURL']
        except PaypalError, e:
            log.error(e)
            self.paypal_email = None
            self.save()
            return None


    @property
    def current_subscription(self):
        subscriptions = self.subscription_set.order_by('-subscription_started')
        if subscriptions:
            return subscriptions[0]
        return None

    @property
    def is_verified(self):
        return paypal_payment.verify_paypal_account(email=self.paypal_email, first_name=self.first_name, last_name=self.last_name)
    
    @property
    def is_valid(self):
        paypal_status = paypal_payment.verify_paypal_account(email=self.paypal_email, first_name=self.first_name, last_name=self.last_name)
        return paypal_status == "VERIFIED" or paypal_status == "UNVERIFIED"

    @property
    def is_confirmed(self):
        return paypal_payment.confirm_paypal_account(self.paypal_email)
    
    def next_billing_date(self):
        from eloue.accounts.management.commands.pro_billing import plus_one_month, minus_one_month
        from django.db.models import Min, Max
        from eloue.products.models import ProductHighlight, ProductTopPosition
        last_billing_date = self.billing_set.aggregate(Max('date'))['date__max']
        if last_billing_date:
            return plus_one_month(last_billing_date)

        first_subscription = self.subscription_set.aggregate(Min('subscription_started'))['subscription_started__min']
        first_topposition = ProductTopPosition.objects.filter(product__owner=self).aggregate(Min('started_at'))['started_at__min']
        first_highlight = ProductHighlight.objects.filter(product__owner=self).aggregate(Min('started_at'))['started_at__min']
        # if he was never billed, we'll use the starting date of the first service used
        started_at_list = filter(None, [first_subscription, first_topposition, first_highlight])
        if started_at_list:
            return min(started_at_list).date()

        # if he uses no service at all, we return None
        return None


    @property
    def response_rate(self):
        from eloue.products.models import MessageThread
        threads = MessageThread.objects.filter(recipient=self).annotate(num_messages=Count('messages'))
        if not threads:
            return 100.0
        threads_num = threads.count()
        answered = threads.filter(num_messages__gt=1)
        answered_num = answered.count()
        return answered_num/float(threads_num)*100.0
    
    @property
    def response_time(self):
        from eloue.products.models import ProductRelatedMessage
        messages = ProductRelatedMessage.objects.select_related().filter(~Q(parent_msg=None), parent_msg__recipient=self, sender=self)
        if not messages:
            return timesince(datetime.datetime.now() - datetime.timedelta(days=1))
        rt = sum([message.sent_at - message.parent_msg.sent_at for message in messages], datetime.timedelta(seconds=0))/len(messages)
        return timesince(datetime.datetime.now() - rt)

    @property
    def average_note(self):
        from eloue.rent.models import BorrowerComment, OwnerComment
        borrower_comments = BorrowerComment.objects.filter(booking__owner=self)
        owner_comments = OwnerComment.objects.filter(booking__borrower=self)

        if borrower_comments:
            queryset = borrower_comments.aggregate(Sum('note'), Count('note'))
            borrower_sum, borrower_count = queryset['note__sum'], queryset['note__count']
        else:
            borrower_sum = 0
            borrower_count = 0
        if owner_comments:
            queryset = owner_comments.aggregate(Sum('note'), Count('note'))
            owner_sum, owner_count = queryset['note__sum'], queryset['note__count']
        else:
            owner_sum = 0
            owner_count = 0

        try:
            avg = (borrower_sum + owner_sum) / (borrower_count + owner_count)
        except:
            avg = 0
        return avg

    def send_activation_email(self):
        context = {
            'patron': self, 
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
        }
        message = create_alternative_email('accounts/emails/activation', context, settings.DEFAULT_FROM_EMAIL, [self.email])
        message.send()

    def send_professional_activation_email(self, *args):
        from eloue.accounts.forms import EmailPasswordResetForm
        form = EmailPasswordResetForm({'email': self.email})
        if form.is_valid():
            form.save(
                email_template_name='accounts/emails/professional_activation_email', 
                use_https=True
            )

    def send_gmail_invite(self, receiver, *args):
        context = {
            'patron': self
        }
        message = create_alternative_email('accounts/emails/gmail_invitation', context, settings.DEFAULT_FROM_EMAIL, [receiver])
        message.send()

    def is_expired(self):
        """
        >>> patron = Patron(date_joined=datetime.datetime.now())
        >>> patron.is_expired()
        False
        >>> patron = Patron(date_joined=datetime.datetime.now() - datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1))
        >>> patron.is_expired()
        True
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return (self.date_joined + expiration_date <= datetime.datetime.now())
    is_expired.boolean = True
    is_expired.short_description = ugettext(u"Expiré")


from datetime import time
HOURS = [(time(h, 0), "%02d:00" % (h,)) for h in xrange(24)]

class OpeningTimes(models.Model):
    patron = models.OneToOneField(Patron, editable=False)

    monday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    monday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    monday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    monday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)
    
    tuesday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    tuesday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)
    
    tuesday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    tuesday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)
    
    wednesday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    wednesday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    wednesday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    wednesday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    thursday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    thursday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    thursday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    thursday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    friday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    friday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    friday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    friday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    saturday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    saturday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    saturday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    saturday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    sunday_opens = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    sunday_closes = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)

    sunday_opens_second = models.TimeField(_(u'De'), choices=HOURS, null=True, blank=True)
    sunday_closes_second = models.TimeField(_(u'à'), choices=HOURS, null=True, blank=True)


class CreditCard(models.Model):
    card_number = models.CharField(max_length=20)
    expires = models.CharField(max_length=4)
    holder = models.OneToOneField(Patron, editable=False, null=True)
    masked_number = models.CharField(max_length=20, blank=False)
    keep = models.BooleanField()
    holder_name = models.CharField(max_length=60, help_text=_(u'Conserver mes coordonnées bancaire'))
    subscriber_reference = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.masked_number

class FacebookSession(models.Model):

    access_token = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField(null=True)
        
    user = models.OneToOneField(Patron, null=True)
    uid = models.CharField(max_length=255, unique=True, null=True)

    provider = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = (('user', 'uid'), ('access_token', 'expires'))

    @property
    def me(self):
        me_dict = cache.get('facebook:me_%s' % self.uid, {})
        if me_dict:
            return me_dict
        # we have to stock it in a local variable, and return the value from that
        # local variable, otherwise this stuff is broken with the dummy cache engine
        me_dict = self.graph_api.get_object("me", fields='picture,email,first_name,last_name,gender,username,location')
        cache.set('facebook:me_%s' % self.uid, me_dict, 0)
        return me_dict
    
    @property
    def graph_api(self):
        if not hasattr(self, '_graph_api') or self._graph_api.access_token != self.access_token:
            self._graph_api = facebook.GraphAPI(self.access_token)
        return self._graph_api
    
class Address(models.Model):
    """An address"""
    patron = models.ForeignKey(Patron, related_name='addresses')
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=9)
    position = models.PointField(null=True, blank=True)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)

    objects = models.GeoManager()

    COUNTRIES = COUNTRY_CHOICES

    class Meta:
        verbose_name_plural = _('addresses')

    def __unicode__(self):
        """
        >>> address = Address(address1='11, rue debelleyme', zipcode='75003', city='Paris')
        >>> address.__unicode__()
        u'11, rue debelleyme  75003 Paris'
        >>> address = Address(address1='11, rue debelleyme', zipcode='75003', city='Paris', position=Point((48.8613232, 2.3631101)))
        >>> address.__unicode__()
        u'11, rue debelleyme  75003 Paris'
        """
        return smart_unicode("%s %s %s %s" % (self.address1, self.address2 if self.address2 else '', self.zipcode, self.city))

    def save(self, *args, **kwargs):
        self.position = self.geocode()
        super(Address, self).save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.position:
            if self.position.x > 90 or self.position.x < -90 or self.position.y < -180 or self.position.y > 180:
                raise ValidationError(_(u"Coordonnées géographiques incorrectes"))

    def geocode(self):
        location = ', '.join(
            filter(
                lambda t: t is not None, 
                [self.address1, self.address2, self.zipcode, self.city, self.country]
            )
        )
        name, (lat, lon), radius = GoogleGeocoder().geocode(location)
        if lat and lon:
            return Point(lat, lon)

    def is_geocoded(self):
        """
        >>> address = Address(address1='11, rue debelleyme', zipcode='75003', city='Paris')
        >>> address.is_geocoded()
        False
        >>> address = Address(address1='11, rue debelleyme', zipcode='75003', city='Paris', position=Point((48.8613232, 2.3631101)))
        >>> address.is_geocoded()
        True
        """
        return self.position != None
    is_geocoded.boolean = True
    is_geocoded.short_description = ugettext(u"Géolocalisé")


class PhoneNumber(models.Model):
    """A phone number"""
    patron = models.ForeignKey(Patron, related_name='phones')
    number = models.CharField(max_length=255)
    kind = models.PositiveSmallIntegerField(choices=PHONE_TYPES, default=PHONE_TYPES.OTHER)

    def __unicode__(self):
        return smart_unicode(self.number)

class PatronAccepted(models.Model):
    """Patron accpeted to create an account for private plateform"""
    email = models.EmailField()
    sites = models.ManyToManyField(Site, related_name='patrons_accepted')

class ProPackage(models.Model):
    name = models.CharField(max_length=64)
    maximum_items = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    valid_from = models.DateField(default=datetime.datetime.now)
    valid_until = models.DateField(null=True, blank=True)

    def __unicode__(self):
        if self.maximum_items:
            return u'{maximum_items} item - {price} euro'.format(maximum_items=self.maximum_items, price=self.price)
        else:
            return u'illimity items - {price} euro'.format(price=self.price)


    class Meta:
        unique_together = (('maximum_items', 'valid_until'), )
        ordering = ('-maximum_items', )
    
class Subscription(models.Model):
    patron = models.ForeignKey(Patron)
    propackage = models.ForeignKey(ProPackage)
    subscription_started = models.DateTimeField(auto_now_add=True)
    subscription_ended = models.DateTimeField(null=True, blank=True)

    def price(self, _from=datetime.datetime.min, to=datetime.datetime.max):
        started_at = _from if _from > self.subscription_started else self.subscription_started
        ended_at = to if not self.subscription_ended or to < self.subscription_ended else self.subscription_ended
        days_num = calendar.monthrange(started_at.year, started_at.month)[1]
        days_sec = days_num * 24 * 60 * 60
        td = (ended_at - started_at)
        dt_sec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        return (self.propackage.price * dt_sec / days_sec).quantize(D('0.01'))

class BillingSubscription(models.Model):
    subscription = models.ForeignKey('Subscription')
    billing = models.ForeignKey('Billing')
    price = models.DecimalField(max_digits=8, decimal_places=2)


class BillingProductHighlight(models.Model):
    producthighlight = models.ForeignKey('products.ProductHighlight')
    billing = models.ForeignKey('Billing')
    price = models.DecimalField(max_digits=8, decimal_places=2)


class BillingProductTopPosition(models.Model):
    producttopposition = models.ForeignKey('products.ProductTopPosition')
    billing = models.ForeignKey('Billing')
    price = models.DecimalField(max_digits=8, decimal_places=2)


class Notification(models.Model):
    patron = models.ForeignKey(Patron)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(editable=False, null=True, blank=True)

    class Meta:
        abstract = True
    def send(self, msg):
        raise NotImplementedError()

class PhoneNotification(Notification):
    phone_number = models.CharField(max_length=64)

    def send(self, msg):
        print 'texto sent'
        PhoneNotificationHistory.objects.create(notification=self)

class EmailNotification(Notification):
    email = models.CharField(max_length=256)

    def __unicode__(self):
        return u"{email}".format(email=self.email)

    def send(self, msg):
        print 'email sent'
        EmailNotificationHistory.objects.create(notification=self)


class PhoneNotificationHistory(models.Model):
    sent_at = models.DateTimeField(auto_now_add=True)
    notification = models.ForeignKey('accounts.PhoneNotification')

    def price(self, date_from, date_to):
        return settings.SMSNOTIFICATION_PRICE.quantize(D('0.01'))

class EmailNotificationHistory(models.Model):
    sent_at = models.DateTimeField(auto_now_add=True)
    notification = models.ForeignKey('accounts.EmailNotification')

    def price(self, date_from, date_to):
        return settings.EMAILNOTIFICATION_PRICE.quantize(D('0.01'))

class BillingPhoneNotification(models.Model):
    phonenotification = models.ForeignKey('accounts.PhoneNotificationHistory')
    billing = models.ForeignKey('accounts.Billing')
    price = models.DecimalField(max_digits=8, decimal_places=2)

class BillingEmailNotification(models.Model):
    emailnotification = models.ForeignKey('accounts.EmailNotificationHistory')
    billing = models.ForeignKey('accounts.Billing')
    price = models.DecimalField(max_digits=8, decimal_places=2)


BILLING_STATE = [('unpaid', 'UNPAID'), ('paid', 'UNPAID')]

class Billing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    patron = models.ForeignKey(Patron)

    # first day of the period
    date = models.DateField()
    state = FSMField(default='unpaid', choices=BILLING_STATE)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    total_tva = models.DecimalField(max_digits=8, decimal_places=2)

    highlights = models.ManyToManyField('products.ProductHighlight', through='BillingProductHighlight')
    plans = models.ManyToManyField('accounts.Subscription', through='BillingSubscription')
    toppositions = models.ManyToManyField('products.ProductTopPosition', through='BillingProductTopPosition')
    
    phonenotifications = models.ManyToManyField('accounts.PhoneNotificationHistory', through='BillingPhoneNotification')
    emailnotifications = models.ManyToManyField('accounts.EmailNotificationHistory', through='BillingEmailNotification')

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    payment = generic.GenericForeignKey('content_type', 'object_id')

    @models.permalink
    def get_absolute_url(self):
        date = self.date
        return (
            'billing_object', (), 
            {'year': '%04d'%date.year, 
             'month': '%02d'%date.month, 
             'day': '%02d'%date.day})

    def pdf(self):
        if self.pk is None:
            raise ValueError('You can generate pdf only for already saved Billings.')
        raise NotImplementedError()

    @transition(source='unpaid', target='paid', save=True)
    def pay(self, **kwargs):
        self.payment.preapproval('billing:%d'%self.id, self.total_amount, None, '')
        self.payment.pay('billing:%d'%self.id, self.total_amount, None, **kwargs)
        self.payment.save()

    @staticmethod
    def builder(patron, date_from, date_to):
        """Returns a (billing, subscriptions, highlights) tuple for a given
        """
        from eloue.products.models import ProductHighlight, ProductTopPosition
        if not isinstance(date_from, datetime.datetime):
            date_from = datetime.datetime.combine(date_from, datetime.time())
        if not isinstance(date_to, datetime.datetime):
            date_to = datetime.datetime.combine(date_to, datetime.time())
        # TODO: verify this logical expression
        highlights = ProductHighlight.objects.select_related('product').filter((
            ~models.Q(ended_at__lte=date_from) & 
            ~models.Q(started_at__gte=date_to) |
            models.Q(ended_at__isnull=True) & 
            models.Q(started_at__lte=date_to)), 
            product__owner=patron)
        subscriptions = Subscription.objects.filter((
            ~models.Q(subscription_ended__lte=date_from) & 
            ~models.Q(subscription_started__gte=date_to) |
            models.Q(subscription_ended__isnull=True) & 
            models.Q(subscription_started__lte=date_to)),
            patron=patron)
        toppositions = ProductTopPosition.objects.select_related('product').filter((
            ~models.Q(ended_at__lte=date_from) & 
            ~models.Q(started_at__gte=date_to) |
            models.Q(ended_at__isnull=True) & 
            models.Q(started_at__lte=date_to)), 
            product__owner=patron)

        phonenotifications = PhoneNotificationHistory.objects.select_related('notification').filter(
            sent_at__gt=date_from, sent_at__lte=date_to, notification__patron=patron)
        emailnotifications = EmailNotificationHistory.objects.select_related('notification').filter(
            sent_at__gt=date_from, sent_at__lte=date_to, notification__patron=patron)

        highlights.sum = sum(map(lambda highlight: highlight.price(date_from, date_to), highlights))
        subscriptions.sum = sum(map(lambda subscription: subscription.price(date_from, date_to), subscriptions))
        toppositions.sum = sum(map(lambda topposition: topposition.price(date_from, date_to), toppositions))
        phonenotifications.sum = sum(map(lambda phonenotification: phonenotification.price(date_from, date_to), phonenotifications))
        emailnotifications.sum = sum(map(lambda emailnotification: emailnotification.price(date_from, date_to), emailnotifications))

        total_amount = (highlights.sum + subscriptions.sum + toppositions.sum + 
            phonenotifications.sum + emailnotifications.sum)
        total_tva = (total_amount * settings.TVA).quantize(D('0.01'))
        return (
            Billing(date=date_from, patron=patron,
                total_amount=total_amount, total_tva=total_tva), 
            highlights, subscriptions, toppositions, 
            phonenotifications, emailnotifications, 
        )


class BillingHistory(models.Model):
    billing = models.ForeignKey('accounts.Billing')
    date = models.DateTimeField(auto_now_add=True)
    succeeded = models.BooleanField()

signals.post_save.connect(post_save_sites, sender=Patron)
signals.pre_delete.connect(pre_delete_creditcard, sender=CreditCard)
signals.post_save.connect(post_save_to_batch_update_product, sender=Address)
signals.post_save.connect(post_save_to_batch_update_product, sender=Patron)
