# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

from storages.backends.s3boto import S3BotoStorage

from eloue.accounts.models import Patron, Address
from eloue.products.fields import SimpleDateField
from eloue.products.manager import ProductManager
from eloue.products.utils import Enum

UNIT = Enum([
    (0, 'HOUR', _(u'heure')),
    (1, 'DAY', _(u'jour')),
    (2, 'WEEK_END', _(u'week-end')),
    (3, 'WEEK', _(u'semaine')),
    (4, 'MONTH', _(u'mois'))
])

CURRENCY = Enum([
    ('EUR', 'EUR', _(u'€')),
    ('USD', 'USD', _(u'$')),
    ('GBP', 'GPB', _(u'£')),
    ('JPY', 'YEN', _(u'¥'))
])

INSURANCE_MAX_DEPOSIT = getattr(settings, 'INSURANCE_MAX_DEPOSIT', 750)

class Product(models.Model):
    """A product"""
    summary = models.CharField(null=False, max_length=255)
    deposit = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    currency = models.CharField(null=False, max_length=3, choices=CURRENCY)
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
    
    def has_insurance(self):
        return not self.owner.is_professional \
            and self.deposit <= INSURANCE_MAX_DEPOSIT \
            and self.category.need_insurance
    
    @property
    def slug(self):
        from django.template.defaultfilters import slugify
        return slugify(self.summary)
    
    @permalink
    def get_absolute_url(self):
        return ('product_detail', [self.slug, self.pk])
    
    class Meta:
        verbose_name = _('product')
    

class Picture(models.Model):
    """A picture"""
    product = models.ForeignKey(Product, related_name='pictures')
    image = models.ImageField(upload_to='pictures/', storage=S3BotoStorage())
    # TODO : We still need to store thumbnails

class Category(models.Model):
    """A category"""
    parent = models.ForeignKey('self', related_name='children', null=True)
    name = models.CharField(null=False, max_length=255)
    slug = models.SlugField(null=False, db_index=True) # TODO : add unique=True
    need_insurance = models.BooleanField(default=True, db_index=True)
    
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
    name = models.CharField(null=True, blank=True, max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(null=False, max_length=3, choices=CURRENCY)
    product = models.ForeignKey(Product, related_name='prices')
    unit = models.IntegerField(choices=UNIT)
    
    started_at = SimpleDateField(null=True, blank=True)
    ended_at = SimpleDateField(null=True, blank=True)
    
    def __unicode__(self):
        return smart_unicode(self.amount)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount < 0:
            raise ValidationError(_(u"Le prix ne peut pas être négatif"))
    
    class Meta:
        unique_together = ('product', 'unit')
    

class Review(models.Model):
    """A review"""
    summary = models.CharField(null=False, blank=True, max_length=255)
    score = models.FloatField(null=False)
    description = models.TextField(null=False)
    created_at = models.DateTimeField(blank=True)
    ip = models.IPAddressField(null=True, blank=True)
    reviewer = models.ForeignKey(Patron, related_name="%(class)s_reviews")
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score > 1:
            raise ValidationError(_("Score can't be higher than 1"))
        if self.score < 0:
            raise ValidationError(_("Score can't be a negative value"))
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        super(Review, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True
    

class ProductReview(Review):
    product = models.ForeignKey(Product, related_name='reviews')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.reviewer == self.product.owner:
            raise ValidationError(_(u"Vous ne pouvez pas commenter vos propres locations"))
        if not self.product.bookings.filter(borrower=self.reviewer).exists():
            raise ValidationError(_(u"Vous ne pouvez pas commenter un produit que vous n'avez pas loué"))
        super(ProductReview, self).clean()
    

class PatronReview(Review):
    patron = models.ForeignKey(Patron, related_name='reviews')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.reviewer == self.patron:
            raise ValidationError(_(u"Vous ne pouvez pas commenter votre profil"))
        if not self.patron.bookings.filter(borrower=self.reviewer).exists():
            raise ValidationError(_(u"Vous ne pouvez pas commenter le profil d'un loueur avec lequel n'avez pas effectué de réservations"))
        super(PatronReview, self).clean()
    
