# -*- coding: utf-8 -*-
import datetime
import logbook
import uuid
import urllib2
import simplejson
import facebook

from imagekit.models import ImageModel

from django.core.exceptions import ValidationError
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db.models import permalink, Q, signals, Count
from django.utils.encoding import smart_unicode
from django.utils.formats import get_format
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.defaultfilters import slugify

from eloue.accounts.manager import PatronManager
from eloue.geocoder import GoogleGeocoder
from eloue.products.utils import Enum
from eloue.signals import post_save_sites
from eloue.utils import create_alternative_email
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

class Avatar(ImageModel):

    patron = models.OneToOneField(User, related_name='avatar')
    image = models.ImageField(upload_to=upload_to)
    created_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        super(Avatar, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Avatar, self).delete(*args, **kwargs)
    
    class IKOptions:
        spec_module = 'eloue.accounts.specs'
        image_field = 'image'
        cache_dir = 'media'
        cache_filename_format = "%(specname)s_%(filename)s.%(extension)s"

class Language(models.Model):

    lang = models.CharField(max_length=30)

    def __unicode__(self):
        return ugettext(self.lang)
    
class Patron(User):
    """A member"""
    civility = models.PositiveSmallIntegerField(_(u"Civilité"), null=True, blank=True, choices=CIVILITY_CHOICES)
    company_name = models.CharField(null=True, blank=True, max_length=255)
    activation_key = models.CharField(null=True, blank=True, max_length=40)
    is_subscribed = models.BooleanField(_(u'newsletter'), default=False, help_text=_(u"Précise si l'utilisateur est abonné à la newsletter"))
    new_messages_alerted = models.BooleanField(_(u'alerts if new messages come'), default=True, help_text=_(u"Précise si l'utilisateur est informé par email s'il a nouveaux messages"))
    is_professional = models.NullBooleanField(_('professionnel'), blank=True, default=None, help_text=_(u"Précise si l'utilisateur est un professionnel"))
    modified_at = models.DateTimeField(_('date de modification'), editable=False)
    affiliate = models.CharField(null=True, blank=True, max_length=10)
    slug = models.SlugField(unique=True, db_index=True)
    paypal_email = models.EmailField(null=True, blank=True)
    sites = models.ManyToManyField(Site, related_name='patrons')
    
    default_address = models.ForeignKey('Address', null=True, blank=True, related_name="+")

    customers = models.ManyToManyField('self', symmetrical=False)

    about = models.TextField(blank=True)
    work = models.CharField(max_length=75, blank=True)
    school = models.CharField(max_length=75, blank=True)
    hobby = models.CharField(max_length=75, blank=True)
    languages = models.ManyToManyField(Language, blank=True)

    on_site = CurrentSiteManager()
    objects = PatronManager()


    def save(self, *args, **kwargs):
        if not self.slug:
            if self.is_professional:
                self.slug = slugify(self.company_name)
            else:
                self.slug = slugify(self.username)
        self.modified_at = datetime.datetime.now()
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
    def is_verified(self):
        return paypal_payment.verify_paypal_account(email=self.paypal_email, first_name=self.first_name, last_name=self.last_name)
    
    @property
    def is_valid(self):
        paypal_status = paypal_payment.verify_paypal_account(email=self.paypal_email, first_name=self.first_name, last_name=self.last_name)
        return paypal_status == "VERIFIED" or paypal_status == "UNVERIFIED"

    @property
    def is_confirmed(self):
        return paypal_payment.confirm_paypal_account(self.paypal_email)
    
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

    def send_activation_email(self):
        context = {
            'patron': self, 'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
        }
        message = create_alternative_email('accounts/activation', context, settings.DEFAULT_FROM_EMAIL, [self.email])
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


signals.post_save.connect(post_save_sites, sender=Patron)
