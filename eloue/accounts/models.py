# -*- coding: utf-8 -*-
import datetime

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

CIVILITY_CHOICES = (
    (0, _('Madame')),
    (1, _('Mademoiselle')),
    (2, _('Monsieur'))
)

COUNTRY_CHOICES = (
    ('FR', _(u'France')),
    ('BE', _(u'Belgique')),
    ('LU', _(u'Luxembourg')),
    ('RE', _(u'Réunion')),
    ('DE', _(u'Allemagne')),
    ('AD', _(u'Andore')),
    ('AT', _(u'Autriche')),
    ('CA', _(u'Canada')),
    ('CY', _(u'Chypre')),
    ('DK', _(u'Danemark')),
    ('ES', _(u'Espagne')),
    ('US', _(u'États-Unis')),
    ('FI', _(u'Finlande')),
    ('GR', _(u'Grèce')),
    ('GP', _(u'Guadeloupe')),
    ('GG', _(u'Guernesey')),
    ('GF', _(u'Guyane Française')),
    ('HU', _(u'Hongrie')),
    ('IE', _(u'Irlande')),
    ('IS', _(u'Islande')),
    ('IT', _(u'Italie')),
    ('JP', _(u'Japon')),
    ('JE', _(u'Jersey')),
    ('LV', _(u'Lettonie')),
    ('LI', _(u'Liechtenstein')),
    ('LT', _(u'Lituanie')),
    ('MT', _(u'Malte')),
    ('MQ', _(u'Martinique')),
    ('MU', _(u'Maurice')),
    ('YT', _(u'Mayotte')),
    ('MC', _(u'Monaco')),
    ('MA', _(u'Maroc')),
    ('NO', _(u'Norvège')),
    ('NC', _(u'Nouvelle-Calédonie')),
    ('NL', _(u'Pays-Bas')),
    ('PL', _(u'Pologne')),
    ('PF', _(u'Polynésie Française')),
    ('PT', _(u'Portugal')),
    ('RO', _(u'Roumanie')),
    ('GB', _(u'Royaume-Uni')),
    ('RU', _(u'Russie, Fédération de')),
    ('PM', _(u'Saint-Pierre-et-Miquelon')),
    ('VA', _(u'Saint-Siège (État de la cité du Vatican)')),
    ('SE', _(u'Suède')),
    ('CH', _(u'Suisse')),
    ('CZ', _(u'Tchèque, République')),
    ('TF', _(u'Terres Australes Françaises')),
    ('TN', _(u'Tunisie')),
    ('TR', _(u'Turquie'))
)

PHONE_TYPES = (
    (0, _('Domicile')),
    (1, _('Travail')),
    (2, _('Mobile')),
    (3, _('Fax')),
    (4, _('Autre'))
)

class Patron(User):
    """A member"""
    civility = models.IntegerField(null=True, blank=True, choices=CIVILITY_CHOICES)
    company_name = models.CharField(null=True, blank=True, max_length=255)
    activation_key = models.CharField(null=True, blank=True, max_length=40)
    is_subscribed = models.BooleanField(_(u'newsletter'), default=False, help_text=_(u"Précise si l'utilisateur est abonné à la newsletter"))
    is_professional = models.BooleanField(_('professionnel'), null=False, default=False, help_text=_(u"Précise si l'utilisateur est un professionnel"))
    modified_at = models.DateTimeField(_('date de modification'), editable=False)
    last_ip = models.IPAddressField(null=True, blank=True)
    slug = models.SlugField(null=False, unique=True, db_index=True)
    
    objects = PatronManager()
    
    def send_activation_email(self):
        subject = render_to_string('auth/activation_email_subject.txt', { 'site':Site.objects.get_current() })
        text_content = render_to_string('auth/activation_email.txt', { 'activation_key':self.activation_key, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS, 'site':Site.objects.get_current() })
        html_content = render_to_string('auth/activation_email.html', { 'activation_key':self.activation_key, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS, 'site':Site.objects.get_current() })
        message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [self.email])
        message.attach_alternative(html_content, "text/html")
        message.send()
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk: # FIXME : Might need some improvements and more tests
            if Patron.objects.exclude(pk=self.pk).filter(email=self.email).exists():
                raise ValidationError(_(u"Un utilisateur utilisant cet email existe déjà"))
        else:
            if Patron.objects.exists(email=self.email):
                raise ValidationError(_(u"Un utilisateur utilisant cet email existe déjà"))
    
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
    
    @permalink
    def get_absolute_url(self):
        return ('patron_detail', [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        self.modified_at = datetime.datetime.now()
        super(Patron, self).save(*args, **kwargs)
    

class Address(models.Model):
    """An address"""
    patron = models.ForeignKey(Patron, related_name='addresses')
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(null=True, max_length=9)
    position = models.PointField(null=True, blank=True)
    city = models.CharField(null=False, max_length=255)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, null=False)
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        """
        >>> address = Address(address1='11, rue debelleyme', zipcode='75003', city='Paris')
        >>> address.__unicode__()
        u'11, rue debelleyme  75003 Paris'
        >>> address = Address(address1='11, rue debelleyme', zipcode='75003', city='Paris', position=Point((48.8613232, 2.3631101)))
        >>> address.__unicode__()
        u'11, rue debelleyme  75003 Paris (48.8613232, 2.3631101)'
        """
        if self.position:
            return smart_unicode("%s %s %s %s (%s, %s)" % (self.address1, self.address2 if self.address2 else '', self.zipcode, self.city, self.position.x, self.position.y))
        else:
            return smart_unicode("%s %s %s %s" % (self.address1, self.address2 if self.address2 else '', self.zipcode, self.city))
    
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
    
    def save(self, *args, **kwargs):
        if not self.position: # TODO : improve that part
            geocode = geocoder(settings.GOOGLE_API_KEY)
            name, (lat, lon) = geocode(smart_str("%s %s %s %s" % (self.address1, self.address2, self.zipcode, self.city)))
            if lat and lon:
                self.position = Point(lat, lon)
        super(Address, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name_plural = _('addresses')
    

class PhoneNumber(models.Model):
    """A phone number"""
    patron = models.ForeignKey(Patron, related_name='phones')
    number = models.CharField(null=False, max_length=255)
    kind = models.IntegerField(choices=PHONE_TYPES)

