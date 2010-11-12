# -*- coding: utf-8 -*-
import datetime
import logbook

from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.gis.geos import Point
from django.core.mail import EmailMultiAlternatives
from django.db.models import permalink
from django.utils.encoding import smart_unicode, smart_str
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

from geocoders.google import geocoder

from eloue.accounts.manager import PatronManager
from eloue.products.utils import Enum
from eloue.rent.paypal import accounts, PaypalError

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

log = logbook.Logger('eloue.accounts')


class Patron(User):
    """A member"""
    civility = models.PositiveSmallIntegerField(null=True, blank=True, choices=CIVILITY_CHOICES)
    company_name = models.CharField(null=True, blank=True, max_length=255)
    activation_key = models.CharField(null=True, blank=True, max_length=40)
    is_subscribed = models.BooleanField(_(u'newsletter'), default=False, help_text=_(u"Précise si l'utilisateur est abonné à la newsletter"))
    is_professional = models.BooleanField(_('professionnel'), default=False, help_text=_(u"Précise si l'utilisateur est un professionnel"))
    modified_at = models.DateTimeField(_('date de modification'), editable=False)
    last_ip = models.IPAddressField(null=True, blank=True)
    slug = models.SlugField(unique=True, db_index=True)
    paypal_email = models.EmailField(null=True, blank=True)
    
    objects = PatronManager()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        self.modified_at = datetime.datetime.now()
        super(Patron, self).save(*args, **kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('patron_detail', [self.slug])
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk: # TODO : Might need some improvements and more tests
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
    
    @property
    def is_verified(self):
        try:
            response = accounts.get_verified_status(
                emailAddress=self.email,
                firstName=self.first_name,
                lastName=self.last_name
            )
            return response['accountStatus'] == 'VERIFIED'
        except PaypalError, e:
            log.error(e)
            return False
    
    def send_activation_email(self):
        subject = render_to_string('accounts/activation_email_subject.txt', {'patron': self, 'site': Site.objects.get_current()})
        text_content = render_to_string('accounts/activation_email.txt', {'patron': self, 'activation_key': self.activation_key, 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS, 'site': Site.objects.get_current()})
        html_content = render_to_string('accounts/activation_email.html', {'patron': self, 'activation_key': self.activation_key, 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS, 'site': Site.objects.get_current()})
        message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [self.email])
        message.attach_alternative(html_content, "text/html")
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
        if not self.position: # TODO : improve that part
            geocode = geocoder(settings.GOOGLE_API_KEY)
            name, (lat, lon) = geocode(smart_str("%s %s %s %s" % (self.address1, self.address2, self.zipcode, self.city)))
            if lat and lon:
                self.position = Point(lat, lon)
        super(Address, self).save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.position:
            if self.position.x > 90 or self.position.x < -90 or self.position.y < -180 or self.position.y > 180:
                raise ValidationError(_(u"Coordonnées géographiques incorrectes"))
    
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
    
