# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

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
    is_professional = models.BooleanField(null=False, default=False)
    company_name = models.CharField(null=True, max_length=255)
    last_ip = models.IPAddressField(null=True)
    modified_at = models.DateTimeField(editable=False)
    
    objects = PatronManager()
    
    def save(self, *args, **kwargs):
        self.modified_at = datetime.datetime.now()
        super(Patron, self).save(*args, **kwargs)
    

class Address(models.Model):
    """An address"""
    patrons = models.ForeignKey(Patron, related_name='addresses')
    civility = models.IntegerField(choices=CIVILITY_CHOICES)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(null=False, max_length=255)
    zipcode = models.CharField(null=True, max_length=255)

class PhoneNumber(models.Model):
    """A phone number"""
    patrons = models.ForeignKey(Patron, related_name='phones')
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
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Patron, self).save(*args, **kwargs)
    
