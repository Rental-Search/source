# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

CIVILITY_CHOICES = (
    (0, 'Madame'),
    (1, 'Mademoiselle'),
    (2, 'Monsieur')
)

PHONE_TYPES = (
    (0, 'Domicile'),
    (1, 'Mobile'),
    (2, 'Fax')
)

class Patron(User):
    """A member"""
    is_professional = models.BooleanField(null=False, default=False)
    company_name = models.CharField(null=True, max_length=255)
    last_ip = models.IPAddressField(null=True)
    modified_at = models.DateTimeField()

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
    score = models.FloatField(null=False)
    description = models.TextField(null=False)
    created_at = models.DateTimeField()
    ip = models.IPAddressField(null=True)
    patron = models.ForeignKey(Patron, related_name='comments')

