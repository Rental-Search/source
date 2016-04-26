# -*- coding: utf-8 -*-
import uuid
from decimal import Decimal as D

from datetime import datetime, timedelta, date
from calendar import monthrange, weekday

import operator
import itertools
from django.core.exceptions import ValidationError
from django.db.models.deletion import PROTECT

from imagekit.models import ImageSpecField
from pilkit import processors

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import connection
from django.db.models import permalink, Q, Avg, Count
from django.db.models.signals import post_save, class_prepared
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_unicode
from django.utils.formats import get_format
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from mptt.models import MPTTModel

from django_messages.models import Message 
from django.db.models import signals

from accounts.models import Patron, Address, ProAgency, PhoneNumber
from products.fields import SimpleDateField
from products.manager import ProductManager, PriceManager, QuestionManager, CurrentSiteProductManager, CurrentSiteProduct2CategoryManager, TreeManager
from products.signals import (post_save_answer, post_save_product, 
    post_save_curiosity, post_save_to_update_product, post_save_message)
from products.choices import UNIT, CURRENCY, STATUS, PAYMENT_TYPE, SEAT_NUMBER, DOOR_NUMBER, CONSUMPTION, FUEL, TRANSMISSION, MILEAGE, CAPACITY, TAX_HORSEPOWER, PRIVATE_LIFE,\
    PROPERTY_TYPES
from rent.contract import ContractGenerator, ContractGeneratorNormal, ContractGeneratorCar, ContractGeneratorRealEstate

from eloue.geocoder import GoogleGeocoder
from eloue.signals import post_save_sites
from eloue import signals as eloue_signals
from eloue.utils import currency, create_alternative_email, itertools_accumulate, convert


import copy
import types
import __builtin__

#http://stackoverflow.com/questions/5614741/cant-use-a-list-of-methods-in-a-python-class-it-breaks-deepcopy-workaround
def _deepcopy_method(x, memo):
    return type(x)(x.im_func, copy.deepcopy(x.im_self, memo), x.im_class)
copy._deepcopy_dispatch[types.MethodType] = _deepcopy_method




INSURANCE_MAX_DEPOSIT = getattr(settings, 'INSURANCE_MAX_DEPOSIT', 750)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
# FIXME: a regression has appeared that get_format() returns values for en-gb instead of fr-fr
DEFAULT_CURRENCY = get_format('CURRENCY', lang=settings.LANGUAGE_CODE) if not settings.CONVERT_XPF else "XPF"

ALERT_RADIUS = getattr(settings, 'ALERT_RADIUS', 200)


@receiver(class_prepared,
    dispatch_uid='products_product_setup_postgres_intarray_class_prepared')
def setup_postgres_intarray(sender, **kwargs):
    """
    Always create PostgreSQL intarray extension if it doesn't already exist
    on the database after model Product has been prepared.
    Requires PostgreSQL 9.1 or newer.
    """
    if sender.__name__ == 'Product':
        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS intarray")
        class_prepared.disconnect(dispatch_uid='products_product_setup_postgres_intarray_class_prepared')


class Product(models.Model):
    """A product"""
    summary = models.CharField(_(u'Titre'), max_length=255)
    deposit_amount = models.DecimalField(_(u'Dépôt de garantie'), max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=DEFAULT_CURRENCY)
    description = models.TextField(blank=True)
    address = models.ForeignKey(Address, related_name='products', on_delete=PROTECT)
    phone = models.ForeignKey(PhoneNumber, related_name='products', null=True, on_delete=PROTECT)
    quantity = models.IntegerField(_(u'Quantité'), default=1)
    shipping = models.BooleanField(_(u'Livraison possible'), default=False)

    is_archived = models.BooleanField(_(u'archivé'), default=False, db_index=True)
    is_allowed = models.BooleanField(_(u'autorisé'), default=True, db_index=True, help_text=_(u"Not index the product in the search engine"))
    # FIXME: 'category' attribute is obsoleted by 'categories' and must be removed
    category = models.ForeignKey('Category', verbose_name=_(u"Catégorie"), related_name='products')
    categories = models.ManyToManyField('Category', related_name='product_categories', through='Product2Category')
    owner = models.ForeignKey(Patron, related_name='products')
    created_at = models.DateTimeField(blank=True, editable=True) # FIXME should be auto_now_add=True
    sites = models.ManyToManyField(Site, related_name='products')
    payment_type = models.PositiveSmallIntegerField(_(u"Type de payments"), default=PAYMENT_TYPE.PAYPAL, choices=PAYMENT_TYPE)
    on_site = CurrentSiteProductManager()
    objects = ProductManager() # FIXME: this should be first manager in the class

    modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    pro_agencies = models.ManyToManyField(ProAgency, related_name='products', blank=True, null=True)

    source = models.ForeignKey(Site, null=True, blank=True)


    class Meta:
        verbose_name = _('product')
    
    def __unicode__(self):
        return smart_unicode(self.summary)
    
    def save(self, *args, **kwargs):
        self.summary = strip_tags(self.summary)
        self.description = strip_tags(self.description)
        if not self.created_at: # FIXME: created_at should be declared with auto_now_add=True
            self.created_at = datetime.now()
            self.source = Site.objects.get_current()
        super(Product, self).save(*args, **kwargs)

    def _get_category(self):
        qs = self.product2category_set.all().select_related('category')
        if settings.DEBUG:
            category_count = qs.count()
            # assert category_count == 1, 'product_id: %d; category_count: %d; site_id: %d' % (self.id, category_count, Site.objects.get_current().id)
        return qs[0].category
    
    def annotate_with_property_values(self):
        properties = self.category.inherited_properties
        for prop in properties:
            setattr(self, prop.prefixed_attr_name, prop.default)
        values = self.properties.all()
        for val in values:
            setattr(self, val.property_type.prefixed_attr_name, val.property_type.value_type_func(val.value))
    
    def fields_from_properties(self, field_map):
        return self.category.fields_from_properties(field_map)
    
    @permalink
    def get_absolute_url(self):
        category = self._get_category()
        ancestors_slug = category.get_ancertors_slug()
        if ancestors_slug:
            path = '%s/%s/' % (ancestors_slug, category.slug)
        else:
            path = '%s/' % self.category.slug
        return 'booking_create', [path, self.slug, self.pk]
    
    def more_like_this(self):
        from products.search import product_search
        sqs = product_search.dwithin(
            'locations', self.address.position,
            Distance(km=DEFAULT_RADIUS)
        ) #.distance('location', self.address.position)
        return sqs.more_like_this(self)[:3]
    
    @property
    def slug(self):
        return slugify(self.summary) or 'none'
    
    @property
    def has_insurance(self):
        return not self.owner.is_professional \
            and self.deposit_amount <= INSURANCE_MAX_DEPOSIT \
            and self.category.need_insurance
    
    @property
    def daily_price(self):
        if not hasattr(self, '_daily_price'):
            self._daily_price = next(itertools.ifilter(lambda price: price.unit == 1, self.prices.all()), None)
        return self._daily_price

    @property
    def local_currency_deposit_amount(self):
        # XXX: ugly and not very well tested hack
        if self.daily_price:
            if self.daily_price.currency == DEFAULT_CURRENCY:
                return self.deposit_amount
            else:
                return convert(self.deposit_amount, DEFAULT_CURRENCY, self.daily_price.currency)
        else:
            return self.deposit_amount 

    @property
    def average_note(self):
        avg = self.borrowercomments.aggregate(Avg('note'))['note__avg']
        return avg or 0

    @property
    def average_rate(self):
        avg = self.borrowercomments.aggregate(Avg('note'))['note__avg']
        return 0 if avg is None else int(round(avg))

    @property
    def comment_count(self):
        return self.borrowercomments.count()

    @property
    def stats(self):
        # TODO: we would need a better rating calculation in the future
        res = self.borrowercomments.aggregate(Avg('note'), Count('id'))
        comment_count = res['id__count'] or 0
        avg = res['note__avg']
        res = {
            'average_rating': 0 if avg is None else int(round(avg)),
            'ratings_count': comment_count,
            'booking_comments_count': comment_count,
            'bookings_count': self.bookings.count(), # expecting Booking.on_site is used as the default manager
        }
        return res

    @property
    def borrowercomments(self):
        from rent.models import BorrowerComment
        return BorrowerComment.objects.filter(booking__product=self)

    @property
    def comment_count(self):
        return self.borrowercomments.count()


    @property
    def shipping_available(self):
        try:
            self.departure_point
        except models.Model.DoesNotExist:
            return False
        return True
    
    def monthly_availability(self, year, month):

        year = int(year)
        month = int(month)
        _, days_num = monthrange(year, month)

        started_at = datetime(year, month, 1, 0, 0)
        ended_at = started_at + timedelta(days=days_num)
        
        # the bookings 
        bookings = self.bookings.filter(
            Q(state="pending")|Q(state="ongoing")
        ).filter(
            ~Q(ended_at__lte=started_at) & ~Q(started_at__gte=ended_at)
        )

        _one_day = timedelta(days=1)
        #day_first = datetime(year, month, 1)

        START = 1
        END = -1
        
        bookings_tuple = [(booking.started_at, booking.ended_at, booking.quantity) for booking in bookings]

        for day in xrange(days_num):
            bookings_tuple += ((
                datetime(year, month, 1 + day), 
                datetime(year, month, 1 + day) + _one_day, 
                0
            ),)
        grouped_dates = itertools.groupby(
            sorted(
                itertools.chain.from_iterable(
                    ((start, START, value), (end, END, value)) 
                    for start, end, value 
                    in bookings_tuple)
            ),
            key=operator.itemgetter(0)
        )
        changements = [
            (key, sum(event[1]*event[2] for event in group))
            for key, group
            in grouped_dates
        ]

        borrowed = zip(
            map(operator.itemgetter(0), changements),
            itertools_accumulate(map(operator.itemgetter(1), changements))
        )
        availables = [(key, self.quantity - value) for key, value in borrowed]
        
        return [
            (d.date(), available) 
            for (d, available) in (
                min(group, key=lambda x: x[1])
                for (key, group) 
                in itertools.groupby(availables, key=lambda x:x[0].date())
                if key.year == year and key.month == month and key >= date.today()
            )
        ]

    @property
    def name(self):
        if self.subtype == self:
            return 'product'
        else:
            return self.subtype.name
    
    @property
    def subtype(self):
        if hasattr(self, '_subtype'):
            return self._subtype
        else:
            try:
                self._subtype = self.carproduct
                if not self._subtype:
                    raise self.DoesNotExist()
            except self.DoesNotExist:
                try:
                    self._subtype = self.realestateproduct
                    if not self._subtype:
                        raise self.DoesNotExist()
                except self.DoesNotExist:
                    self._subtype = self
        return self._subtype

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
        if self.category.need_insurance and settings.INSURANCE_AVAILABLE:
            return ContractGeneratorNormal()
        else:
            return ContractGenerator()

    @property
    def is_highlighted(self):
        return bool(self.producthighlight_set.filter(ended_at__isnull=True).only('id')[:1])

    @property
    def is_top(self):
        return bool(self.producttopposition_set.filter(ended_at__isnull=True).only('id')[:1])


    def calculate_price(self, started_at, ended_at):
        # It doesn't play well with season
        prices = {price.unit: price.day_amount for price in self.prices.all()}
        if not prices:
            return None, None

        try:
            amount, unit = D(0), prove_price_unit(prices, started_at, ended_at)
        except Exception, e:
            raise Exception(
                    u'{0} Product: {1}, prices: {2}, started_at: {3}, ended_at: {4}'.
                    format(str(e), self.id, prices, started_at, ended_at))

        package = UNIT.package[unit]
        delta = ended_at - started_at

        for price in self.prices.filter(unit=unit, started_at__isnull=False, ended_at__isnull=False):
            price_delta = price.delta(started_at, ended_at)
            delta -= price_delta
            amount += package(price.day_amount, price_delta, False)

        if delta.days > 0 or delta.seconds > 0:
            try:
                price = self.prices.get(unit=unit, started_at__isnull=True, ended_at__isnull=True)
            except Price.MultipleObjectsReturned:
                price = self.prices.filter(unit=unit, started_at__isnull=True, ended_at__isnull=True)[0]
            null_delta = timedelta(days=0)
            amount += package(price.day_amount, null_delta if null_delta > delta else delta)

        return unit, amount.quantize(D(".00"))

def prove_price_unit(prices, started_at, ended_at):
    delta = ended_at - started_at
    delta_days = delta.days

    if delta_days < 4 and delta_days >= 2 and \
        weekday(started_at.year, started_at.month, started_at.day) >= 4 and \
        weekday(ended_at.year, ended_at.month, ended_at.day) in (0, 6) and \
        UNIT.WEEK_END in prices:
        price_package = UNIT.WEEK_END

    elif delta_days >= monthrange(started_at.year, started_at.month)[1] and UNIT.MONTH in prices:
        price_package = UNIT.MONTH

    elif delta_days >= 15 and UNIT.FIFTEEN_DAYS in prices:
        price_package = UNIT.FIFTEEN_DAYS

    elif delta_days >= 14 and UNIT.TWO_WEEKS in prices:
        price_package = UNIT.TWO_WEEKS

    elif delta_days >= 7 and UNIT.WEEK in prices:
        price_package = UNIT.WEEK

    elif delta_days >= 3 and UNIT.THREE_DAYS in prices:
        price_package = UNIT.THREE_DAYS

    elif delta_days < 1 and delta.seconds > 0 and UNIT.HOUR in prices:
        price_package = UNIT.HOUR

    elif UNIT.DAY in prices:
        price_package = UNIT.DAY

    else:
        raise Exception('No price package could be proven.')

    return price_package


class CarProduct(Product):

    brand = models.CharField(_(u'marque'), max_length=30)
    model = models.CharField(_(u'modèle'), max_length=30)

    # charactersitiques du vehicule
    seat_number = models.IntegerField(_(u'nombre de place'), null=True, blank=True, choices=SEAT_NUMBER, default=4)
    door_number = models.IntegerField(_(u'nombre de porte'), null=True, blank=True, choices=DOOR_NUMBER, default=5)
    fuel = models.IntegerField(_(u'énergie'), choices=FUEL, null=True, blank=True, default=1)
    transmission = models.IntegerField(_(u'boite de vitesse'), choices=TRANSMISSION, null=True, blank=True, default=1)
    mileage = models.IntegerField(_(u'kilométrage'), choices=MILEAGE, null=True, blank=True, default=2)
    consumption = models.PositiveIntegerField(_(u'consommation'), null=True, blank=True, choices=CONSUMPTION, default=4)

    # info about km included
    km_included = models.PositiveIntegerField(_(u'kilomètres inclus/jour'), null=True, blank=True, help_text=_(u'Nombre de kilomètres maximum que le locataire peut effectuer par jour.'))
    costs_per_km = models.DecimalField(_(u'Prix par kilomètres supplémentaires'), null=True, blank=True, max_digits=8, decimal_places=3, help_text=_(u'Prix du kilomètre supplémentaire. Si le locataire dépasse le nombre de kilomètre inclus par jour.'))

    # options & accessoires
    air_conditioning = models.NullBooleanField(_(u'climatisation'))
    power_steering = models.NullBooleanField(_(u'direction assistée'))
    cruise_control = models.NullBooleanField(_(u'régulateur de vitesse'))
    gps = models.NullBooleanField(_(u'GPS'))
    baby_seat = models.NullBooleanField(_(u'siège bébé'))
    roof_box = models.NullBooleanField(_(u'coffre de toit'))
    bike_rack = models.NullBooleanField(_(u'porte-vélo'))
    snow_tires = models.NullBooleanField(_(u'pneus neige'))
    snow_chains = models.NullBooleanField(_(u'chaines'))
    ski_rack = models.NullBooleanField(_(u'porte-skis'))
    cd_player = models.NullBooleanField(_(u'lecteur CD'))
    audio_input = models.NullBooleanField(_(u'entrée audio/iPod'))

    # informations de l'assurance
    tax_horsepower = models.PositiveIntegerField(_(u'CV fiscaux'), choices=TAX_HORSEPOWER)
    licence_plate = models.CharField(_(u"N° d'immatriculation"), max_length=10)
    first_registration_date = models.DateField(_(u'1er mise en circulation'))

    objects = ProductManager()
    on_site = CurrentSiteProductManager()

    def licence_plate_is_peer(self):
        from products.fields import old_plate_re, new_plate_re

        if not self.licence_plate:
            return None

        matches = old_plate_re.match(self.licence_plate)

        if matches:
            num = int(matches.groups()[0])
        else:
            matches = new_plate_re.match(self.licence_plate)
            if matches:
                num = int(matches.groups()[1])
            else:
                return None

        if num % 2 == 0:
            return True
        else:
            return False

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
    def name(self):
        return 'carproduct'

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
        if self.category.need_insurance and settings.INSURANCE_AVAILABLE:
            return ContractGeneratorCar()
        else:
            return ContractGenerator()

class RealEstateProduct(Product):
    
    capacity = models.IntegerField(_(u'capacité'), null=True, blank=True, choices=CAPACITY, default=1, help_text=_(u'Nombre de personne que peux accueillir votre locgement'))
    private_life = models.IntegerField(_(u'Type de logement'),
        choices=PRIVATE_LIFE, null=True, blank=True, default=1)
    chamber_number = models.IntegerField(_(u'nombre de chambre'), null=True, blank=True, choices=CAPACITY, default=1)
    rules = models.TextField(_(u"Règles d'utilisation"), max_length=60, null=True, blank=True)

    # service_included
    air_conditioning = models.NullBooleanField(_(u'air conditionné'))
    breakfast = models.NullBooleanField(_(u'petit déjeuner'))
    balcony = models.NullBooleanField(_(u'balcon/terasse'))
    lockable_chamber = models.NullBooleanField(_(u'chambre avec serrure'))
    towel = models.NullBooleanField(_(u'serviettes'))
    lift = models.NullBooleanField(_(u'ascenseur dans l\'immeuble'))
    family_friendly = models.NullBooleanField(_(u'adapté aux familles/enfants'))
    gym = models.NullBooleanField(_(u'salle de sport'))
    accessible = models.NullBooleanField(_(u'accessible aux personnes handicapées'))
    heating = models.NullBooleanField(_(u'chauffage'))
    jacuzzi = models.NullBooleanField(_(u'jacuzzi'))
    chimney = models.NullBooleanField(_(u'cheminée intérieure'))
    internet_access = models.NullBooleanField(_(u'accès internet'))
    kitchen = models.NullBooleanField(_(u'cuisine'))
    parking = models.NullBooleanField(_(u'parking'))
    smoking_accepted = models.NullBooleanField(_(u'fumeurs acceptées'))
    ideal_for_events = models.NullBooleanField(_(u'idéal pour des évènements'))
    tv = models.NullBooleanField(_(u'TV'))
    washing_machine = models.NullBooleanField(_(u'machine à laver'))
    tumble_dryer = models.NullBooleanField(_(u'sèche linge'))
    computer_with_internet = models.NullBooleanField(_(u'ordinateur avec Internet'))

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
    def name(self):
        return 'realestateproduct'
        
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
        if self.category.need_insurance and settings.INSURANCE_AVAILABLE:
            return ContractGeneratorRealEstate()
        else:
            return ContractGenerator()

def upload_to(instance, filename):
    return 'pictures/%s.jpg' % uuid.uuid4().hex


class Picture(models.Model):
    """A picture"""
    product = models.ForeignKey(Product, related_name='pictures', blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to=upload_to)
    created_at = models.DateTimeField(blank=True, editable=False)

    thumbnail = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=100, height=100),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )
    profile = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=300, height=300),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )

    vertical_profile = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=225, height=325),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )

    home = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=180, height=120),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )
    display = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=450, height=300),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )

    db_display = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=450, height=650),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )



    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        super(Picture, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Picture, self).delete(*args, **kwargs)
    

def category_upload_to(instance, filename):
    return 'pictures/categories/%s.jpg' % uuid.uuid4().hex


class Category(MPTTModel):
    """A category"""
    parent = models.ForeignKey('self', related_name='childrens', blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True)
    need_insurance = models.BooleanField(default=True, db_index=True)
    sites = models.ManyToManyField(Site, related_name='categories')

    # fields moved from CategoryDescription
    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=category_upload_to)

    profile = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=1920, height=400),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )

    thumbnail = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=226, height=159),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )

    home = ImageSpecField(
        source='image',
        processors=[
            processors.Transpose(processors.Transpose.AUTO),
            processors.SmartResize(width=265, height=250),
            processors.Adjust(contrast=1.2, sharpness=1.1),
        ],
    )

    on_site = CurrentSiteManager()
    objects = models.Manager()
    tree = TreeManager()

    product = models.OneToOneField(Product, related_name='category_product', null=True, blank=True)
    
    @property
    def inherited_properties(self):
        res = {}
        for cat in self.get_ancestors(include_self=True)\
                        .prefetch_related('properties').order_by('level'):
            res.update({prop.prefixed_attr_name:prop for prop in cat.properties.all()})
        return res.values()

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
            slug = slugify(self.name)
            if Category.on_site.filter(slug=slug).exists():
                raise ValidationError(_(u'Category with name %s (%s) already exists. Site_id is %d.') % (self.name, slug, Site.objects.get_current().id))
            self.slug = slug
        super(Category, self).save(*args, **kwargs)

    def get_conformity(self, site_id):
        if site_id in self.sites.all().values_list('id', flat=True):
            return self

        category = self
        conformity = None
        eloue_site_id = 1
        gosport_site_id = 13
        dressbooking_site_id = 15
        while category and not conformity:
            try:
                conformity = CategoryConformity.objects.filter(
                    Q(gosport_category=category) | Q(eloue_category=category)
                )[0]
            except IndexError:
                category = category.parent

        if not conformity:
            return None
        else:
            conformity_category = conformity.eloue_category if site_id == eloue_site_id else conformity.gosport_category if site_id == gosport_site_id else conformity.gosport_category if site_id == dressbooking_site_id else None
            if conformity_category and conformity_category.sites.filter(pk=site_id):
                return conformity_category
            else:
                return None

    def get_ancertors_slug(self):
        return '/'.join(el.slug for el in self.get_ancestors()).replace(' ', '')
    
    
    def get_algolia_path(self):
        return " > ".join([cat.name+'|'+str(cat.id)\
                           for cat in self.get_ancestors(include_self=True)])
    
    @classmethod
    def from_algolia_path(clazz, path):
        parts = path.split()
        
    
    def get_absolute_url(self):
        ancestors_slug = self.get_ancertors_slug()
        if ancestors_slug:
            return u"/%(location)s/%(ancestors_slug)s/%(slug)s/" % {'location': _('location'), 'ancestors_slug': ancestors_slug, 'slug': self.slug }
        else:
            return u"/%(location)s/%(slug)s/" % {'location': _('location'), 'slug': self.slug}
        
    def fields_from_properties(self, field_map):
        prop_fields = {p.prefixed_attr_name:field_map[p.value_type if not p.choices_str else 'choice'](property_type=p)
            for p in self.inherited_properties}
        return prop_fields


class Product2Category(models.Model):
    product = models.ForeignKey('Product')
    category = models.ForeignKey('Category', related_name='+')
    site = models.ForeignKey('sites.Site', related_name='+')

    on_site = CurrentSiteProduct2CategoryManager()
    objects = models.Manager()

# TODO: enable unique SQL DB constraint
#    class Meta:
#        unique_together = ('product', 'category', 'site')

class CategoryConformity(models.Model):
    eloue_category = models.ForeignKey('Category', related_name='+')
    gosport_category = models.ForeignKey('Category', related_name='+')


forbidden_property_names = dir(Product)\
     + list(f.name for f in Product._meta.fields)\
     + list(f.name for f in Product._meta.virtual_fields)
     

def validate_property_name(val):
    if val in forbidden_property_names:
        raise ValidationError("Attribute name {} collides with "\
                              +"Product model attribute of the same name".format(val))


class Property(models.Model):
    """
    A category-specific product property 
    
    Stores data useful for creation of:
     * Serialiazer fields
     * SearchIndex fields
     * product editing widgets
     * filter widgets
    """

    CHOICES_SEPARATOR = ','
    PREFIX = 'eloue_'
    
    category = models.ForeignKey(Category, verbose_name=_(u"Catégorie"), related_name='properties')
    name = models.CharField(verbose_name=_(u"Nom affiché"), max_length=255)
    attr_name = models.CharField(verbose_name=_(u"Nom de l'attribut"), max_length=255, \
                                 validators=[validate_property_name,])
    value_type = models.CharField(verbose_name=_(u"Type de la proprieté"), max_length=255, choices=PROPERTY_TYPES, 
                                  default='str')
    
    faceted = models.BooleanField(verbose_name=_(u"Facet"), default=False,
                                  help_text=u"Le proprité est un facet lors de recherches ")
    
    default_str = models.CharField(verbose_name=_(u"Valeur par defaut"), max_length=255, null=True, blank=True)
    max_str = models.CharField(verbose_name=_(u"Valeur maximale"), max_length=255, null=True, blank=True)
    min_str = models.CharField(verbose_name=_(u"Valeur minimale"), max_length=255, null=True, blank=True)
    choices_str = models.CharField(verbose_name=_(u"Valeurs permis"), max_length=255, null=True, blank=True,
                                   help_text=u"Des valeurs separés par \"%s\""%CHOICES_SEPARATOR)
    
    
    @property
    def value_type_func(self):
        func = smart_unicode if self.value_type=='str' \
            else getattr(__builtin__, self.value_type)
        return lambda x: func(x) if x is not None else None
    
    min = property(fget=lambda self:self.value_type_func(self.min_str), 
                   fset=lambda self, val:setattr(self, 'min_str', smart_unicode(val)))
    
    max = property(fget=lambda self:self.value_type_func(self.max_str), 
                   fset=lambda self, val:setattr(self, 'max_str', smart_unicode(val)))
    
    default = property(fget=lambda self:self.value_type_func(self.default_str), 
                   fset=lambda self, val:setattr(self, 'default_str', smart_unicode(val)))
    
    def _get_choices(self):
        if self.choices_str is None:
            return None
        return (self.value_type_func(c.strip()) 
                for c in self.choices_str.split(self.CHOICES_SEPARATOR))
    
    def _set_choices(self, choices):
        if type(choices) not in (list, tuple, None):
            raise ValueError('Wrong value type')
        if not choices:
            self.choices_str = None
        else:
            try:
                map(self.value_type_func, choices)
            except:
                raise Exception('Wrong choice format for type %s' % self.value_type)
            self.choices_str = self.CHOICES_SEPARATOR.join(map(str, choices))
    
    choices = property(fget=_get_choices, fset=_set_choices)
    
    def _get_prefixed_attr_name(self):
        return self.PREFIX + self.attr_name
    
    def _set_prefixed_attr_name(self, val):
        if val.startswith(self.PREFIX):
            return val[len(self.PREFIX):]
        else:
            raise ValueError('Attribute name missing prefix')
    
    prefixed_attr_name = property(fget=_get_prefixed_attr_name,
                                  fset=_set_prefixed_attr_name)
    
    @classmethod
    def get_attr_names(clazz, faceted=True):
        """
        Return all property attr_name values for this site
        """
        cats = Category.objects.filter(sites=settings.SITE_ID).values_list('pk', flat=True)
        attrs = clazz.objects.filter(category_id__in=cats, faceted=faceted).distinct('attr_name')
        return {a.prefixed_attr_name for a in attrs}
        
    
    class Meta:
        verbose_name_plural = _('properties')
        unique_together = (('category', 'attr_name'), ('category', 'name'))
        
    
    def __unicode__(self):
        """
        >>> property = Property(name="Marque")
        >>> property.__unicode__()
        u'Marque'
        """
        return smart_unicode(self.name)


class PropertyValue(models.Model):
    property_type = models.ForeignKey(Property, related_name='values')
    value_str = models.CharField(max_length=255)
    product = models.ForeignKey(Product, related_name='properties')
    
    value = property(fget=lambda self:self.property_type.value_type_func(self.value_str), 
               fset=lambda self, val:setattr(self, 'value_str', smart_unicode(val)))
    
    class Meta:
        unique_together = ('property_type', 'product')
    
    def __unicode__(self):
        """
        >>> property = PropertyValue(value="Mercedes")
        >>> property.__unicode__()
        u'Mercedes'
        """
        return smart_unicode(self.value_str)

class UnavailabilityPeriod(models.Model):
    """A period of time when the product is marked as uniavailable."""
    product = models.ForeignKey('Product')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    quantity = models.PositiveIntegerField(default=1)

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
        return UNIT.units[self.unit](self.local_currency_amount)
    
    def __unicode__(self):
        return smart_unicode(currency(self.local_currency_amount))
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount <= 0:
            raise ValidationError({'amount': _(u"Le prix ne peut pas être négatif")})
    
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
    
    @property
    def local_currency_amount(self):
        # XXX: ugly and not very well tested hack
        if self.currency == DEFAULT_CURRENCY:
            return self.amount
        else:
            return convert(self.amount, DEFAULT_CURRENCY, self.currency)

    def get_prefixed_unit_display(self):
        return UNIT.prefixed[self.unit]

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
    last_offer = models.OneToOneField('ProductRelatedMessage', blank=True, null=True, related_name='last_offer_in_thread') # FIXME: I didn't find any use of this field besides post_save_message() signal handler I've introduced
    subject = models.CharField(_("Subject"), max_length=120)
    sender_archived = models.BooleanField(_("Archived"), default=False)
    recipient_archived = models.BooleanField(_("Archived"), default=False)
    
    def __unicode__(self):
        return unicode(self.subject)

    @permalink
    def get_absolute_url(self):
        return 'messages', [self.pk]

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
    # remove django-messages signal handler
    from django_messages import utils
    signals.post_save.disconnect(utils.new_message_email, sender=Message)

    # add our handler to send messages in both .txt/.html variants
    from products.signals import new_message_email
    signals.post_save.connect(
        new_message_email, sender=Message,
        dispatch_uid='django_messagee.Message-post_save-eloue.legacy.new_message_email'
    )

    # register post-save for our custom ProductRelatedMessage model (derived from Message)
    signals.post_save.connect(
        new_message_email, sender=ProductRelatedMessage,
        dispatch_uid='django_messagee.ProductRelatedMessage-post_save-eloue.legacy.new_message_email'
    )

    # register pre-processing filters for both ProductRelatedMessage and Message
    signals.pre_save.connect(eloue_signals.message_content_filter, sender=ProductRelatedMessage)
    signals.pre_save.connect(eloue_signals.message_site_filter, sender=ProductRelatedMessage) 
    signals.pre_save.connect(eloue_signals.message_content_filter, sender=Message)
    signals.pre_save.connect(eloue_signals.message_site_filter, sender=Message)


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
        name, coords, radius = GoogleGeocoder().geocode(self.location)
        if all(coords):
            return Point(coords)
    
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


class ProductHighlight(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(editable=False, null=True, blank=True)
    product = models.ForeignKey(Product, editable=False)

    def price(self, _from=datetime.min, to=datetime.max):
        started_at = _from if (_from > self.started_at) else self.started_at
        ended_at = to if (not self.ended_at or to < self.ended_at) else self.ended_at
        days_num = monthrange(started_at.year, started_at.month)[1]
        days_sec = days_num * 24 * 60 * 60

        td = (ended_at - started_at)
        dt_sec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        return (settings.PRODUCTHIGHLIGHT_PRICE * dt_sec / days_sec).quantize(D('0.01'))


class ProductTopPosition(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(editable=False, null=True, blank=True)
    product = models.ForeignKey(Product, editable=False)

    def price(self, _from=datetime.min, to=datetime.max):
        started_at = _from if (_from > self.started_at) else self.started_at
        ended_at = to if (not self.ended_at or to < self.ended_at) else self.ended_at
        days_num = monthrange(started_at.year, started_at.month)[1]
        days_sec = days_num * 24 * 60 * 60

        td = (ended_at - started_at)
        dt_sec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        return (settings.PRODUCTTOPPOSITION_PRICE * dt_sec / days_sec).quantize(D('0.01'))


post_save.connect(post_save_answer, sender=Answer,
        dispatch_uid='products_answer_post_save_answer')
post_save.connect(post_save_product, sender=Product,
        dispatch_uid='products_product_post_save_product')
post_save.connect(post_save_product, sender=CarProduct,
        dispatch_uid='products_carproduct_post_save_product')
post_save.connect(post_save_product, sender=RealEstateProduct,
        dispatch_uid='products_realestateproduct_post_save_product')
post_save.connect(post_save_curiosity, sender=Curiosity)

post_save.connect(post_save_sites, sender=Alert)
post_save.connect(post_save_sites, sender=Curiosity)
# post_save.connect(post_save_sites, sender=Category)

# TODO Remove these?
post_save.connect(post_save_to_update_product, sender=Price,
        dispatch_uid='products_price_post_save_to_update_product')
post_save.connect(post_save_to_update_product, sender=Picture,
        dispatch_uid='products_picture_post_save_to_update_product')
post_save.connect(post_save_to_update_product, sender=ProductHighlight,
        dispatch_uid='products_producthighlight_post_save_to_update_product')
post_save.connect(post_save_to_update_product, sender=ProductTopPosition,
        dispatch_uid='products_producttopposition_post_save_to_update_product')

# register a signal handler to update message thread and parent of the newly created message
post_save.connect(post_save_message, sender=ProductRelatedMessage)
