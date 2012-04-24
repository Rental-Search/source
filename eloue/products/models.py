# -*- coding: utf-8 -*-
import uuid
from decimal import Decimal as D

from datetime import datetime, timedelta, time

from imagekit.models import ImageSpec
from imagekit.processors import resize, Adjust, Transpose

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db.models import permalink, Q, Avg
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_unicode
from django.utils.formats import get_format
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from mptt.models import MPTTModel

from eloue.accounts.models import Patron, Address
from eloue.geocoder import GoogleGeocoder
from eloue.products.fields import SimpleDateField
from eloue.products.manager import ProductManager, PriceManager, QuestionManager, CurrentSiteProductManager, TreeManager
from eloue.products.signals import post_save_answer, post_save_product, post_save_curiosity, pre_save_product
from eloue.products.utils import Enum
from eloue.signals import post_save_sites
from eloue.rent.contract import ContractGeneratorNormal, ContractGeneratorCar, ContractGeneratorRealEstate
from django_messages.models import Message 
from eloue.accounts.models import Patron
from django.db.models import signals
from eloue import signals as eloue_signals

from eloue.utils import currency, create_alternative_email, cache_to

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

PAYMENT_TYPE = Enum([
    (0, 'NOPAY', _(u'Le locataire me paye directement et mon objet n\'est pas assuré')),
    (1, 'PAYPAL', _(u'Le locataire paye en ligne et mon objet est assuré')),
    (2, 'PAYBOX', _(u'Le locataire paye en ligne par son carte bancaire et mon objet est assuré')),
])

SEAT_NUMBER = Enum([
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')),
    (7, '7', _(u'7')),
    (8, '8', _(u'8')),
    (9, '9', _(u'9')),
    (10, '10', _(u'10')),
])

DOOR_NUMBER = Enum([
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')),
])

CONSUMPTION = Enum([
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')), 
    (7, '7', _(u'7')),
    (8, '8', _(u'8')),
    (9, '9', _(u'9')),
    (10, '10', _(u'10')),
    (11, '11', _(u'11')),
    (12, '12', _(u'12')),
    (13, '13', _(u'13')),
    (14, '14', _(u'14')),
    (15, '15', _(u'15')),
    (16, '16', _(u'16')),
    (17, '17', _(u'17')),
    (18, '18', _(u'18')),
    (19, '19', _(u'19')),
])

FUEL = Enum ([
    (1, '1', _(u'Essence')),
    (2, '2', _(u'Diesel')),
    (3, '3', _(u'GPL')),
    (4, '4', _(u'Electrique')),
    (5, '5', _(u'Hybride')),
])

TRANSMISSION = Enum ([
    (1, '1', _(u'Manuel')),
    (2, '2', _(u'Automatique')),
])

MILEAGE = Enum ([
    (1, '1', _(u'- de 10000 km')),
    (2, '2', _(u'Entre 10001 et 50000 km')),
    (3, '3', _(u'Plus de 50000 km')),
])

CAPACITY = Enum ([
    (1, '1', _(u'1')),
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')), 
    (7, '7', _(u'7')),
    (8, '8', _(u'8')),
    (9, '9', _(u'9')),
    (10, '10', _(u'10')),
    (11, '11', _(u'11')),
    (12, '12', _(u'12')),
    (13, '13', _(u'13')),
    (14, '14', _(u'14')),
    (15, '15', _(u'15')),
    (16, '16', _(u'16')),
    (17, '17', _(u'17')),
    (18, '18', _(u'18')),
    (19, '19', _(u'19+')),
])

TAX_HORSEPOWER = CAPACITY

PRIVATE_LIFE = Enum([
    (1, '1', _(u'Appartement')),
    (2, '2', _(u'Maison')),
    (3, '3', _(u'Chambre privée')),
])


INSURANCE_MAX_DEPOSIT = getattr(settings, 'INSURANCE_MAX_DEPOSIT', 750)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
DEFAULT_CURRENCY = get_format('CURRENCY') if not settings.CONVERT_XPF else "XPF"

ALERT_RADIUS = getattr(settings, 'ALERT_RADIUS', 200)


class Product(models.Model):
    """A product"""
    summary = models.CharField(_(u'Titre'), max_length=255)
    deposit_amount = models.DecimalField(_(u'Dépôt de garantie'), max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=DEFAULT_CURRENCY)
    description = models.TextField()
    address = models.ForeignKey(Address, related_name='products')
    quantity = models.IntegerField(_(u'Quantité'), default=1)

    is_archived = models.BooleanField(_(u'archivé'), default=False, db_index=True)
    is_allowed = models.BooleanField(_(u'autorisé'), default=True, db_index=True)
    category = models.ForeignKey('Category', verbose_name=_(u"Catégorie"), related_name='products')
    owner = models.ForeignKey(Patron, related_name='products')
    created_at = models.DateTimeField(blank=True, editable=False)
    sites = models.ManyToManyField(Site, related_name='products')
    payment_type = models.PositiveSmallIntegerField(_(u"Type de payments"), default=PAYMENT_TYPE.PAYPAL, choices=PAYMENT_TYPE)
    on_site = CurrentSiteProductManager()
    objects = ProductManager()
    
    modified_at = models.DateTimeField(blank=True, null=True)

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
        encestors_slug = self.category.get_ancertors_slug()
        if encestors_slug:
            path = '%s/%s/' % (self.category.get_ancertors_slug(), self.category.slug)
        else:
            path = '%s/' % self.category.slug
        return ('booking_create', [path, self.slug, self.pk])
    
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
    
    @property
    def daily_price(self):
        return self.prices.get(unit=UNIT.DAY)

    @property
    def average_note(self):
        from eloue.rent.models import BorrowerComment
        return BorrowerComment.objects.filter(booking__product=self).aggregate(Avg('note'))['note__avg']
    
    @property
    def borrowercomments(self):
        from eloue.rent.models import BorrowerComment
        return BorrowerComment.objects.filter(booking__product=self)
    
    def monthly_availability(self):
        import calendar
        from django.db.models import Q
        import operator
        import datetime
        import itertools
        month = 1
        year = 2012

        _, days_num = calendar.monthrange(year, month)

        started_at = datetime.datetime.combine(datetime.date(year, month, 1), datetime.time())
        ended_at = datetime.datetime.combine(datetime.date(year, month, 1), datetime.time()) + datetime.timedelta(days=days_num)
        def _accumulate(iterable, func=operator.add, start=None):
            """
            Modified version of Python 3.2's itertools.accumulate.
            """
            # accumulate([1,2,3,4,5]) --> 0 1 3 6 10 15
            # accumulate([1,2,3,4,5], operator.mul) --> 0 1 2 6 24 120
            # yield 0
            it = iter(iterable)
            total = next(it)
            yield total
            for element in it:
                total = func(total, element)
                yield total
            yield
        
        bookings = self.bookings.filter(
            Q(state="pending")|Q(state="ongoing")
        ).filter(
            ~Q(ended_at__lte=started_at) & ~Q(started_at__gte=ended_at)
        )

        _one_day = datetime.timedelta(days=1)
        day_first = datetime.datetime.combine(datetime.date(year, month, 1), datetime.time())

        START = 1
        END = -1
        
        bookings_tuple = [(booking.started_at, booking.ended_at, booking.quantity) for booking in bookings]

        for day in xrange(days_num):
            midnight = day_first + datetime.timedelta(days=day)
            bookings_tuple += ((midnight, midnight + _one_day, 0), )
        
        grouped_dates = itertools.groupby(
            sorted(
                itertools.chain.from_iterable(
                    ((start, START, value), (end, END, value)) for start, end, value in bookings_tuple), 
                key=operator.itemgetter(0)
            ), key=operator.itemgetter(0)
        )
        
        changements = [
            (key, sum(event[1]*event[2] for event in group))
            for key, group
            in grouped_dates]
        availables = zip(
            map(operator.itemgetter(0), changements), 
            _accumulate(map(operator.itemgetter(1), changements))
        )
        return [
            max(group, key=lambda x: x[1])
            for (key, group) 
            in itertools.groupby(availables, key=lambda x:x[0].date())
            if key.year == year and key.month == month and key >= datetime.date.today()]

    @property
    def subtype(self):
        try:
            return self.carproduct
        except self.DoesNotExist:
            pass
        try:
            return self.realestateproduct
        except self.DoesNotExist:
            pass
        return self

    @property
    def commission(self):
        return settings.COMMISSION

    @property
    def insurance_fee(self):
        return settings.INSURANCE_FEE_NORMAL

    @property
    def insurance_taxes(self):
        return settings.INSURANCE_TAXES_NORMAL

    @property
    def insurance_commission(self):
        return settings.INSURANCE_COMMISSION_NORMAL

    @property
    def contract_generator(self):
        return ContractGeneratorNormal()

class CarProduct(Product):

    brand = models.CharField(_(u'marque'), max_length=30)
    model = models.CharField(_(u'modèle'), max_length=30)

    # charactersitiques du vehicule
    seat_number = models.IntegerField(_(u'nombre de siège'), null=True, blank=True, choices=SEAT_NUMBER, default=4)
    door_number = models.IntegerField(_(u'nombre de porte'), null=True, blank=True, choices=DOOR_NUMBER, default=5)
    fuel = models.IntegerField(_(u'énergie'), choices=FUEL, null=True, blank=True, default=1)
    transmission = models.IntegerField(_(u'boite de vitesse'), choices=TRANSMISSION, null=True, blank=True, default=1)
    mileage = models.IntegerField(_(u'kilométrage'), choices=MILEAGE, null=True, blank=True, default=2)
    consumption = models.PositiveIntegerField(_(u'consommation'), null=True, blank=True, choices=CONSUMPTION, default=4)

    # options & accessoires
    air_conditioning = models.BooleanField(_(u'climatisation'))
    power_steering = models.BooleanField(_(u'direction assistée'))
    cruise_control = models.BooleanField(_(u'régulateur de vitesse'))
    gps = models.BooleanField(_(u'GPS'))
    baby_seat = models.BooleanField(_(u'siège bébé'))
    roof_box = models.BooleanField(_(u'coffre de toit'))
    bike_rack = models.BooleanField(_(u'porte-vélo'))
    snow_tires = models.BooleanField(_(u'pneus neige'))
    snow_chains = models.BooleanField(_(u'chaines'))
    ski_rack = models.BooleanField(_(u'porte-skis'))
    cd_player = models.BooleanField(_(u'lecteur CD'))
    audio_input = models.BooleanField(_(u'entrée audio/iPod'))

    # informations de l'assurance
    tax_horsepower = models.PositiveIntegerField(_(u'CV fiscal'), choices=TAX_HORSEPOWER)
    licence_plate = models.CharField(_(u"N° d'immatriculation"), max_length=10)
    first_registration_date = models.DateField(_(u'1er mise en circulation'))

    objects = ProductManager()
    on_site = CurrentSiteProductManager()

    @property
    def options(self):
        option_names = [
            field.name 
            for field in self.__class__._meta.fields 
            if isinstance(field, models.BooleanField) and field.model == self.__class__
        ]
        return [
            self._meta.get_field(field_name).verbose_name 
            for field_name in option_names 
            if getattr(self, field_name)
        ]

    @property
    def subtype(self):
        return self

    @property
    def commission(self):
        return settings.COMMISSION

    @property
    def insurance_fee(self):
        return settings.INSURANCE_FEE_CAR

    @property
    def insurance_taxes(self):
        return settings.INSURANCE_TAXES_CAR

    @property
    def insurance_commission(self):
        return settings.INSURANCE_COMMISSION_CAR

    @property
    def contract_generator(self):
        return ContractGeneratorCar()

class RealEstateProduct(Product):
    
    capacity = models.IntegerField(_(u'capacité'), null=True, blank=True, choices=CAPACITY, default=1, help_text=_(u'Nombre de personne que peux accueillir votre locgement'))
    private_life = models.IntegerField(_(u'vie privée'),
        choices=PRIVATE_LIFE, null=True, blank=True, default=1)
    chamber_number = models.IntegerField(_(u'nombre de chambre'), null=True, blank=True, choices=CAPACITY, default=1)
    rules = models.TextField(_(u"règle d'utilisation"), max_length=60, null=True, blank=True)

    # service_included
    air_conditioning = models.BooleanField(_(u'air conditionné'))
    breakfast = models.BooleanField(_(u'petit déjeuner'))
    balcony = models.BooleanField(_(u'balcon/terasse'))
    lockable_chamber = models.BooleanField(_(u'chambre avec serrure'))
    towel = models.BooleanField(_(u'serviettes'))
    lift = models.BooleanField(_(u'ascenseur dans l\'immeuble'))
    family_friendly = models.BooleanField(_(u'adapté aux familles/enfants'))
    gym = models.BooleanField(_(u'salle de sport'))
    accessible = models.BooleanField(_(u'accessible aux personnes handicapées'))
    heating = models.BooleanField(_(u'chauffage'))
    jacuzzi = models.BooleanField(_(u'jacuzzi'))
    chimney = models.BooleanField(_(u'cheminée intérieure'))
    internet_access = models.BooleanField(_(u'accès internet'))
    kitchen = models.BooleanField(_(u'cuisine'))
    parking = models.BooleanField(_(u'parking'))
    smoking_accepted = models.BooleanField(_(u'fumeurs acceptées'))
    ideal_for_events = models.BooleanField(_(u'idéal pour des évènements'))
    tv = models.BooleanField(_(u'TV'))
    washing_machine = models.BooleanField(_(u'machine à laver'))
    tumble_dryer = models.BooleanField(_(u'sèche linge'))
    computer_with_internet = models.BooleanField(_(u'ordinateur avec Internet'))

    objects = ProductManager()
    on_site = CurrentSiteProductManager()
    
    @property
    def options(self):
        option_names = [
            field.name 
            for field in self.__class__._meta.fields 
            if isinstance(field, models.BooleanField) and field.model == self.__class__
        ]
        return [
            self._meta.get_field(field_name).verbose_name 
            for field_name in option_names 
            if getattr(self, field_name)
        ]

    @property
    def subtype(self):
        return self

    @property
    def commission(self):
        return settings.COMMISSION

    @property
    def insurance_fee(self):
        return settings.INSURANCE_FEE_REALESTATE

    @property
    def insurance_taxes(self):
        return settings.INSURANCE_TAXES_REALESTATE

    @property
    def insurance_commission(self):
        return settings.INSURANCE_COMMISSION_REALESTATE

    @property
    def contract_generator(self):
        return ContractGeneratorRealEstate()

def upload_to(instance, filename):
    return 'pictures/%s.jpg' % uuid.uuid4().hex


class Picture(models.Model):
    """A picture"""
    product = models.ForeignKey(Product, related_name='pictures', blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to=upload_to)
    created_at = models.DateTimeField(blank=True, editable=False)

    thumbnail = ImageSpec(
        processors=[
            resize.Crop(width=60, height=60), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=False, cache_to=cache_to
    )
    profile = ImageSpec(
        processors=[
            resize.Crop(width=200, height=170), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=False, cache_to=cache_to
    )
    home = ImageSpec(
        processors=[
            resize.Crop(width=120, height=140), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=False, cache_to=cache_to
    )
    display = ImageSpec(
        processors=[
            resize.Fit(width=578, height=500), 
            Adjust(contrast=1.2, sharpness=1.1),
            Transpose(Transpose.AUTO),
        ], image_field='image', pre_cache=False, cache_to=cache_to
    )

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        super(Picture, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Picture, self).delete(*args, **kwargs)
    

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
    
    def get_ancertors_slug(self):
        return ''.join('%s/' %  el.slug for el in self.get_ancestors()).replace(' ', '')[:-1]
    
    def get_absolute_url(self):
        ancestors_slug = self.get_ancertors_slug()
        if ancestors_slug:
            return _(u"/location/%(ancestors_slug)s/%(slug)s/") % {
                        'ancestors_slug': ancestors_slug,
                        'slug': self.slug
                    }
        else:
            return _(u"/location/%(slug)s/") % {
                        'slug': self.slug
                    }
            

class CategoryDescription(models.Model):
    category = models.OneToOneField(Category, related_name='description')

    title = models.CharField(max_length=150)
    description = models.TextField()
    header = models.TextField()
    footer = models.TextField()
    
    def __unicode__(self):
        return "%s - %s"%(self.category.name, self.title)
    

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
    
    @property
    def day_amount(self):
        return UNITS[self.unit](self.amount)
    
    def __unicode__(self):
        return smart_unicode(currency(self.amount))
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount <= 0:
            raise ValidationError(_(u"Le prix ne peut pas être négatif"))
    
    def delta(self, started_at, ended_at):
        """Return delta of time passed in this season price"""
        increase = 0
        if self.ended_at < self.started_at:
            increase = 1
        if ended_at >= self.ended_at.datetime(ended_at.year + increase) + timedelta(days=1):
            ended_at = self.ended_at.datetime(ended_at.year + increase) + timedelta(days=1)
        if started_at <= self.started_at.datetime(started_at.year):
            started_at = self.started_at.datetime(started_at.year)
        delta = (ended_at - started_at)
        return delta if delta > timedelta(days=0) else timedelta(days=0)
    
    class Meta:
        ordering = ['unit']


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
        

class MessageThread(models.Model):
    sender = models.ForeignKey(Patron, related_name='initiated_threads')
    recipient = models.ForeignKey(Patron, related_name='participating_threads')
    product = models.ForeignKey(Product, related_name='messages', blank=True, null=True) # we should remove NULL after migration of the data
    last_message = models.OneToOneField('ProductRelatedMessage', blank=True, null=True, related_name='last_message_in_thread')
    last_offer = models.OneToOneField('ProductRelatedMessage', blank=True, null=True, related_name='last_offer_in_thread')
    subject = models.CharField(_("Subject"), max_length=120)
    sender_archived = models.BooleanField(_("Archived"), default=False)
    recipient_archived = models.BooleanField(_("Archived"), default=False)
    
    def __unicode__(self):
        return unicode(self.subject)
    
    def new_recipient(self):
        """Returns True if self.recipient has unread message in the thread
        """
        return self.last_message.recipient == self.recipient and not self.last_message.read_at
    
    def new_sender(self):
        """Return True if self.sender has unread message in the thread
        """
        return self.last_message.recipient == self.sender and not self.last_message.read_at


class ProductRelatedMessage(Message):

    thread = models.ForeignKey(MessageThread, related_name='messages', blank=True, null=True) # we should remove NULL after migration of the data
    offer = models.OneToOneField('rent.Booking', blank=True, null=True, related_name='offer_in_message')

    def __unicode__(self):
        return self.body

if "notification" not in settings.INSTALLED_APPS:
    from django_messages import utils
    signals.post_save.connect(utils.new_message_email, sender=ProductRelatedMessage)
    signals.pre_save.connect(eloue_signals.message_content_filter, sender=ProductRelatedMessage)
    signals.pre_save.connect(eloue_signals.message_site_filter, sender=ProductRelatedMessage) 


class Alert(models.Model):
    patron = models.ForeignKey(Patron, related_name='alerts')
    designation = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(editable=False)
    address = models.ForeignKey(Address, related_name='alerts')
    sites = models.ManyToManyField(Site, related_name='alerts')
    
    on_site = CurrentSiteManager()
    objects = models.Manager()
    
    def __unicode__(self):
        return smart_unicode(self.designation)
    
    def geocode(self):
        name, (lat, lon), radius = GoogleGeocoder().geocode(self.location)
        if lat and lon:
            return Point(lat, lon)
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        super(Alert, self).save(*args, **kwargs)
    
    @property
    def position(self):
        return self.address.position
    
    @property
    def nearest_patrons(self):
        if self.position:
            nearest_addresses = Address.objects.distance(self.position).filter(position__distance_lt=(self.position, Distance(km=ALERT_RADIUS))).order_by('distance')
            return Patron.objects.distinct().filter(addresses__in=nearest_addresses)[:10]
        else:
            return None 

    def send_alerts(self):
        if self.nearest_patrons:
            for patron in self.nearest_patrons:
                message = create_alternative_email('products/emails/alert', {
                    'patron': patron,
                    'alert': self
                    }, settings.DEFAULT_FROM_EMAIL, [self.patron.email])
                message.send()
    
    def send_alerts_answer(self, product):
        message = create_alternative_email('products/emails/alert_answer', {
            'product': product,
            'alert': self
        }, settings.DEFAULT_FROM_EMAIL, [self.patron.email])
        message.send()
            
    @permalink
    def get_absolute_url(self):
        return ('alert_inform', [self.pk])
    
    class Meta:
        get_latest_by = 'created_at'
    

post_save.connect(post_save_answer, sender=Answer)
post_save.connect(post_save_product, sender=Product)
post_save.connect(post_save_curiosity, sender=Curiosity)
post_save.connect(post_save_sites, sender=Alert)
post_save.connect(post_save_sites, sender=Curiosity)
post_save.connect(post_save_sites, sender=Product)
post_save.connect(post_save_sites, sender=Category)
post_save.connect(post_save_sites, sender=CarProduct)
post_save.connect(post_save_sites, sender=RealEstateProduct)
signals.pre_save.connect(pre_save_product, sender=Product)
