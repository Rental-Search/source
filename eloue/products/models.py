# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

from storages.backends.image import ImageStorage

from eloue.accounts.models import Address

UNIT_CHOICES = (
    (0, _('heure')),
    (1, _('jour')),
    (2, _('week-end')),
    (3, _('semaine')),
    (4, _('mois'))
)

class Product(models.Model):
    """A product"""
    summary = models.CharField(null=False, max_length=255)
    deposit = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    description = models.TextField(null=False)
    location = models.ForeignKey(Address, related_name='products')
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField(null=False)
    category = models.ForeignKey('Category', related_name='products')
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    class Meta:
        verbose_name = _('product')

class Picture(models.Model):
    """A picture"""
    product = models.ForeignKey(Product, related_name='pictures')
    image = models.ImageField(upload_to='pictures/', storage=ImageStorage()) # TODO : This might not be ideal

class Category(models.Model):
    """A category"""
    parent = models.ForeignKey('self', related_name='children')
    name = models.CharField(null=False, max_length=255)
    
    def __unicode__(self):
        return smart_unicode(self.name)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

class Property(models.Model):
    """A property"""
    category = models.ForeignKey(Category, related_name='properties')
    name = models.CharField(null=False, max_length=255)
    
    def __unicode__(self):
        return smart_unicode(self.name)
    
    class Meta:
        verbose_name_plural = _('properties')
    

class PropertyValue(models.Model):
    property = models.ForeignKey(Property, related_name='values')
    value = models.CharField(null=False, max_length=255)
    product = models.ForeignKey(Product, related_name='properties')
    
    def __unicode__(self):
        return smart_unicode(self.value)
    
    class Meta:
        unique_together = ('property', 'product')
    

class Price(models.Model):
    """A price"""
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    product = models.ForeignKey(Product, related_name='%(class)s')
    
    def __unicode__(self):
        return smart_unicode(self.amount)
    
    class Meta:
        abstract = True

class SeasonalPrice(Price):
    """A season"""
    name = models.CharField(null=False, max_length=255)
    started_at = models.DateTimeField(null=False)
    ended_at = models.DateTimeField(null=False)

class StandardPrice(Price):
    unit = models.IntegerField(choices=UNIT_CHOICES)

class Review(models.Model):
    """A review"""
    summary = models.CharField(null=False, blank=True, max_length=255)
    score = models.FloatField(null=False)
    description = models.TextField(null=False)
    created_at = models.DateTimeField()
    ip = models.IPAddressField(null=True)
    product = models.ForeignKey(Product, related_name='reviews')
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Review, self).save(*args, **kwargs)
    
