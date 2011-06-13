# -*- coding: utf-8 -*-
import uuid

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db.models import permalink
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_unicode
from django.utils.formats import get_format
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from mptt.models import MPTTModel
from imagekit.models import ImageModel

from eloue.accounts.models import Patron, Address
from eloue.products.fields import SimpleDateField
from eloue.products.manager import ProductManager, PriceManager, QuestionManager, CurrentSiteProductManager, TreeManager
from eloue.products.signals import post_save_answer, post_save_product, post_save_curiosity
from eloue.products.utils import Enum
from eloue.signals import post_save_sites
from eloue.utils import currency
from django_messages.models import Message 
from eloue.accounts.models import Patron

from django.db.models import signals
from eloue import signals as eloue_signals

UNIT = Enum([
    (0, 'HOUR', _(u'heure')),
    (1, 'DAY', _(u'jour')),
    (2, 'WEEK_END', _(u'week-end')),
    (3, 'WEEK', _(u'semaine')),
    (4, 'TWO_WEEKS', _(u'deux semaines')),
    (5, 'MONTH', _(u'mois'))
])

UNITS = {
    0: lambda amount: amount,
    1: lambda amount: amount,
    2: lambda amount: amount,
    3: lambda amount: amount / 7,
    4: lambda amount: amount / 14,
    5: lambda amount: amount / 30,
}

CURRENCY = Enum([
    ('EUR', 'EUR', _(u'€')),
    ('USD', 'USD', _(u'$')),
    ('GBP', 'GPB', _(u'£')),
    ('JPY', 'YEN', _(u'¥')),
    ('XPF', 'XPF', _(u'F'))
])

STATUS = Enum([
    (0, 'DRAFT', _(u'brouillon')),
    (1, 'PRIVATE', _(u'privé')),
    (2, 'PUBLIC', _(u'public')),
    (3, 'REMOVED', _(u'supprimé'))
])

INSURANCE_MAX_DEPOSIT = getattr(settings, 'INSURANCE_MAX_DEPOSIT', 750)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
DEFAULT_CURRENCY = get_format('CURRENCY') if not settings.CONVERT_XPF else "XPF"


class Product(models.Model):
    """A product"""
    summary = models.CharField(max_length=255)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=DEFAULT_CURRENCY)
    description = models.TextField()
    address = models.ForeignKey(Address, related_name='products')
    quantity = models.IntegerField()
    is_archived = models.BooleanField(_(u'archivé'), default=False, db_index=True)
    is_allowed = models.BooleanField(_(u'autorisé'), default=True, db_index=True)
    category = models.ForeignKey('Category', related_name='products')
    owner = models.ForeignKey(Patron, related_name='products')
    created_at = models.DateTimeField(blank=True, editable=False)
    sites = models.ManyToManyField(Site, related_name='products')
    
    on_site = CurrentSiteProductManager()
    objects = ProductManager()
    
    class Meta:
        verbose_name = _('product')
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    def save(self, *args, **kwargs):
        self.summary = strip_tags(self.summary)
        self.description = strip_tags(self.description)
        if not self.created_at:
            self.created_at = datetime.now()
        super(Product, self).save(*args, **kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('booking_create', [self.slug, self.pk])
    
    def more_like_this(self):
        from eloue.products.search_indexes import product_search
        return product_search.spatial(
            lat=self.address.position.x, long=self.address.position.y,
            radius=DEFAULT_RADIUS, unit='km'
        ).more_like_this(self)[:3]
    
    @property
    def slug(self):
        return slugify(self.summary)
    
    @property
    def has_insurance(self):
        return not self.owner.is_professional \
            and self.deposit_amount <= INSURANCE_MAX_DEPOSIT \
            and self.category.need_insurance
    

def upload_to(instance, filename):
    return 'pictures/%s.jpg' % uuid.uuid4().hex


class Picture(ImageModel):
    """A picture"""
    product = models.ForeignKey(Product, related_name='pictures', blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to=upload_to)
    created_at = models.DateTimeField(blank=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        super(Picture, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Picture, self).delete(*args, **kwargs)
    
    class IKOptions:
        spec_module = 'eloue.products.specs'
        image_field = 'image'
        cache_dir = 'media'
        cache_filename_format = "%(specname)s_%(filename)s.%(extension)s"
    

class Category(MPTTModel):
    """A category"""
    parent = models.ForeignKey('self', related_name='childrens', blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    need_insurance = models.BooleanField(default=True, db_index=True)
    sites = models.ManyToManyField(Site, related_name='categories')
    
    on_site = CurrentSiteManager()
    objects = models.Manager()
    tree = TreeManager()
    
    class Meta:
        ordering = ['name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __unicode__(self):
        """
        >>> category = Category(name='Travaux - Bricolage')
        >>> category.__unicode__()
        u'Travaux - Bricolage'
        """
        return smart_unicode(self.name)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return _(u"/location/par-categorie/%(category)s/") % {
            'category': self.slug
        }
    

class Property(models.Model):
    """A property"""
    category = models.ForeignKey(Category, related_name='properties')
    name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = _('properties')
    
    def __unicode__(self):
        """
        >>> property = Property(name="Marque")
        >>> property.__unicode__()
        u'Marque'
        """
        return smart_unicode(self.name)
    

class PropertyValue(models.Model):
    property = models.ForeignKey(Property, related_name='values')
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product, related_name='properties')
    
    class Meta:
        unique_together = ('property', 'product')
    
    def __unicode__(self):
        """
        >>> property = PropertyValue(value="Mercedes")
        >>> property.__unicode__()
        u'Mercedes'
        """
        return smart_unicode(self.value)

class Price(models.Model):
    """A price"""
    name = models.CharField(blank=True, max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=DEFAULT_CURRENCY)
    product = models.ForeignKey(Product, related_name='prices')
    unit = models.PositiveSmallIntegerField(choices=UNIT, db_index=True)
    
    started_at = SimpleDateField(null=True, blank=True)
    ended_at = SimpleDateField(null=True, blank=True)
    
    objects = PriceManager()
    
    class Meta:
        unique_together = ('product', 'unit', 'name')
    
    @property
    def day_amount(self):
        return UNITS[self.unit](self.amount)
    
    def __unicode__(self):
        return smart_unicode(currency(self.amount))
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount < 0:
            raise ValidationError(_(u"Le prix ne peut pas être négatif"))
    
    def delta(self, started_at, ended_at):
        """Return delta of time passed in this season price"""
        increase = 0
        if self.ended_at < self.started_at:
            increase = 1
        if ended_at >= self.ended_at.datetime(ended_at.year + increase):
            ended_at = self.ended_at.datetime(ended_at.year + increase) + timedelta(days=1)
        if started_at <= self.started_at.datetime(started_at.year):
            started_at = self.started_at.datetime(started_at.year) - timedelta(days=1)
        delta = (ended_at - started_at)
        return delta if delta > timedelta(days=0) else timedelta(days=0)
    

class Review(models.Model):
    """A review"""
    summary = models.CharField(blank=True, max_length=255)
    score = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(blank=True, editable=False)
    ip = models.IPAddressField(null=True, blank=True)
    reviewer = models.ForeignKey(Patron, related_name="%(class)s_reviews")
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        super(Review, self).save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score > 1:
            raise ValidationError(_("Score can't be higher than 1"))
        if self.score < 0:
            raise ValidationError(_("Score can't be a negative value"))
    

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
    

class Question(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(editable=False)
    modified_at = models.DateTimeField(editable=False)
    status = models.PositiveSmallIntegerField(choices=STATUS, db_index=True, default=STATUS.DRAFT)
    
    product = models.ForeignKey(Product, related_name="questions")
    author = models.ForeignKey(Patron, related_name="questions")
    
    objects = QuestionManager()
    
    class Meta:
        ordering = ('modified_at', 'created_at')
        get_latest_by = 'modified_at'
    
    def __unicode__(self):
        """
        >>> question = Question(text='Quel est le nombre de place de cette voiture ?')
        >>> question.__unicode__()
        u'Quel est le nombre de place de cette voiture ?'
        """
        return smart_unicode(self.text)
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        else:
            self.modified_at = datetime.now()
        super(Question, self).save(*args, **kwargs)
    

class Answer(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(editable=False)
    question = models.ForeignKey(Question, related_name="answers")
    
    def __unicode__(self):
        """
        >>> answer = Answer(text='Cette voiture comporte 5 places')
        >>> answer.__unicode__()
        u'Cette voiture comporte 5 places'
        """
        return smart_unicode(self.text)
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        super(Answer, self).save(*args, **kwargs)
    

class Curiosity(models.Model):
    product = models.ForeignKey(Product, related_name='curiosities')
    sites = models.ManyToManyField(Site, related_name='curiosities')
    
    on_site = CurrentSiteManager()
    objects = models.Manager()
    
    def __unicode__(self):
        return smart_unicode(self.product.summary)
    
    class Meta:
        verbose_name_plural = "curiosities"
        
class ProductRelatedMessage(Message):
    product = models.ForeignKey(Product, related_name='messages', blank=True, null=True)
    
    
if "notification" not in settings.INSTALLED_APPS:
    from django_messages import utils
    signals.post_save.connect(utils.new_message_email, sender=ProductRelatedMessage)
    signals.pre_save.connect(eloue_signals.message_content_filter, sender=ProductRelatedMessage)
    signals.pre_save.connect(eloue_signals.message_site_filter, sender=ProductRelatedMessage) 

post_save.connect(post_save_answer, sender=Answer)
post_save.connect(post_save_product, sender=Product)
post_save.connect(post_save_curiosity, sender=Curiosity)
post_save.connect(post_save_sites, sender=Curiosity)
post_save.connect(post_save_sites, sender=Product)
post_save.connect(post_save_sites, sender=Category)
