# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from eloue.accounts.manager import PatronManager

CIVILITY_CHOICES = (
    (0, _('Madame')),
    (1, _('Mademoiselle')),
    (2, _('Monsieur'))
)

PHONE_TYPES = (
    (0, _('Domicile')),
    (1, _('Mobile')),
    (2, _('Fax'))
)

class Patron(User):
    """A member"""
    activation_key = models.CharField(max_length=40)
    is_professional = models.BooleanField(null=False, default=False)
    company_name = models.CharField(null=True, max_length=255)
    last_ip = models.IPAddressField(null=True)
    modified_at = models.DateTimeField(editable=False)
    
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
        return self.activation_key == "ALREADY_ACTIVATED" or (self.date_joined + expiration_date <= datetime.datetime.now())
    is_expired.boolean = True
    is_expired.short_description = "expired"
    
    def save(self, *args, **kwargs):
        self.modified_at = datetime.datetime.now()
        super(Patron, self).save(*args, **kwargs)
    

class Address(models.Model):
    """An address"""
    patron = models.ForeignKey(Patron, related_name='addresses')
    civility = models.IntegerField(choices=CIVILITY_CHOICES)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(null=False, max_length=255)
    zipcode = models.CharField(null=True, max_length=255)

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
    ip = models.IPAddressField(null=True)
    patron = models.ForeignKey(Patron, related_name='comments')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if 0 < self.score > 1:
            raise ValidationError(_("Score isn't between 0 and 1"))
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Comment, self).save(*args, **kwargs)
    
