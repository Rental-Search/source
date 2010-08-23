# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

from storages.backends.image import ImageStorage

from eloue.accounts.models import Patron, Address
from eloue.products.manager import ProductManager

UNIT_CHOICES = (
    (0, _('heure')),
    (1, _('jour')),
    (2, _('week-end')),
    (3, _('semaine')),
    (4, _('mois'))
)

CURRENCY_CHOICES = (
    ('EUR', _(u'€')),
    ('USD', _(u'$')),
    ('GBP', _(u'£')),
    ('JPY', _(u'¥'))
)

class Product(models.Model):
    """A product"""
    summary = models.CharField(null=False, max_length=255)
    deposit = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    description = models.TextField(null=False)
    address = models.ForeignKey(Address, related_name='products')
    quantity = models.IntegerField(null=False)
    is_archived = models.BooleanField(_(u'archivé'), default=False, db_index=True)
    is_allowed = models.BooleanField(_(u'autorisé'), default=True, db_index=True)
    category = models.ForeignKey('Category', related_name='products')
    owner = models.ForeignKey(Patron, related_name='products')
    
    objects = ProductManager()
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.address.patron != self.owner:
            raise ValidationError(_(u"L'adresse n'appartient pas au propriétaire de l'objet"))
    
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
    parent = models.ForeignKey('self', related_name='children', null=True)
    name = models.CharField(null=False, max_length=255)
    slug = models.SlugField(null=False)
    
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
    currency = models.CharField(null=False, max_length=3, choices=CURRENCY_CHOICES)
    product = models.ForeignKey(Product, related_name='%(class)s')
    
    def __unicode__(self):
        return smart_unicode(self.amount)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount < 0:
            raise ValidationError(_(u"Le prix ne peut pas être négatif"))
    
    class Meta:
        abstract = True
    

class SeasonalPrice(Price):
    """A season"""
    name = models.CharField(null=False, max_length=255)
    started_at = models.DateTimeField(null=False)
    ended_at = models.DateTimeField(null=False)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.started_at >= self.ended_at:
            raise ValidationError(_(u"Une saison ne peut pas terminer avant d'avoir commencer"))
    
    class Meta:
        unique_together = ('product', 'name')
    

class StandardPrice(Price):
    unit = models.IntegerField(choices=UNIT_CHOICES)
    
    class Meta:
        unique_together = ('product', 'unit')
    

class Review(models.Model):
    """A review"""
    summary = models.CharField(null=False, blank=True, max_length=255)
    score = models.FloatField(null=False)
    description = models.TextField(null=False)
    created_at = models.DateTimeField(blank=True)
    ip = models.IPAddressField(null=True, blank=True)
    product = models.ForeignKey(Product, related_name='reviews')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score > 1:
            raise ValidationError(_("Score can't be higher than 1"))
        if self.score < 0:
            raise ValidationError(_("Score can't be a negative value"))
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.datetime.now()
        super(Review, self).save(*args, **kwargs)
    
