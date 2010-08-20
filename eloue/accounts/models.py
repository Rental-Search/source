# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.loader import render_to_string

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
    activation_key = models.CharField(null=True, blank=True, max_length=40)
    is_professional = models.BooleanField(_('professionnel'), null=False, default=False)
    company_name = models.CharField(null=True, max_length=255)
    last_ip = models.IPAddressField(null=True)
    modified_at = models.DateTimeField(_('date de modification'), editable=False)
    
    objects = PatronManager()
    
    def send_activation_email(self):
        subject = render_to_string('auth/activation_email_subject.txt', { 'site':Site.objects.get_current() })
        text_content = render_to_string('auth/activation_email.txt', { 'activation_key':self.activation_key, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS, 'site':Site.objects.get_current() })
        html_content = render_to_string('auth/activation_email.html', { 'activation_key':self.activation_key, 'expiration_days':settings.ACCOUNT_ACTIVATION_DAYS, 'site':Site.objects.get_current() })
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
        return self.activation_key == None or (self.date_joined + expiration_date <= datetime.datetime.now())
    is_expired.boolean = True
    is_expired.short_description = ugettext(u"Expiré")
    
    def save(self, *args, **kwargs):
        self.modified_at = datetime.datetime.now()
        super(Patron, self).save(*args, **kwargs)
    

class Address(models.Model):
    """An address"""
    patron = models.ForeignKey(Patron, related_name='addresses')
    civility = models.IntegerField(null=True, blank=True, choices=CIVILITY_CHOICES)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(null=True, max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    city = models.CharField(null=False, max_length=255)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, null=False)

class PhoneNumber(models.Model):
    """A phone number"""
    patron = models.ForeignKey(Patron, related_name='phones')
    number = models.CharField(null=False, max_length=255)
    kind = models.IntegerField(choices=PHONE_TYPES)

class Comment(models.Model):
    """A comment"""
    summary = models.CharField(null=False, max_length=255)
    score = models.FloatField(null=False)
    description = models.TextField(null=False)
    created_at = models.DateTimeField()
    ip = models.IPAddressField(null=True, blank=True)
    patron = models.ForeignKey(Patron, related_name='comments')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score > 1:
            raise ValidationError(_("Score can't be higher than 1"))
        if self.score < 0:
            raise ValidationError(_("Score can't be a negative value"))
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Comment, self).save(*args, **kwargs)
    
