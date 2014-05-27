#-*- coding: utf-8 -*-
import datetime
from urlparse import urljoin

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from haystack.sites import site
from haystack.indexes import CharField, DateTimeField, DateField, FloatField, MultiValueField, EdgeNgramField, IntegerField, DecimalField, BooleanField
from haystack.exceptions import AlreadyRegistered
from haystack.query import SearchQuerySet

from queued_search.indexes import QueuedSearchIndex

from products.models import Alert, Product, CarProduct, RealEstateProduct
from rent.models import Booking

__all__ = ['ProductIndex', 'product_search', 'product_only_search', 'AlertIndex', 'alert_search', 'car_search', 'realestate_search']


class ProductIndex(QueuedSearchIndex):
    categories = MultiValueField(faceted=True)
    created_at = DateTimeField(model_attr='created_at')
    created_at_date = DateField()
    description = EdgeNgramField(model_attr='description')
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    city = CharField(model_attr='address__city', indexed=False)
    zipcode = CharField(model_attr='address__zipcode', indexed=False)
    owner = CharField(model_attr='owner__username', faceted=True)
    owner_url = CharField(model_attr='owner__get_absolute_url', indexed=False)
    owner_avatar = CharField()
    price = FloatField(faceted=True)
    sites = MultiValueField(faceted=True)
    summary = EdgeNgramField(model_attr='summary')
    text = CharField(document=True, use_template=True)
    url = CharField(model_attr='get_absolute_url', indexed=False)
    thumbnail = CharField(indexed=False)
    profile = CharField(indexed=False)
    special = BooleanField()
    pro = BooleanField(model_attr='owner__is_professional', default=False)
    
    is_highlighted = BooleanField(model_attr='is_highlighted')
    is_top = BooleanField(model_attr='is_top')

    
    def prepare_sites(self, obj):
        return [site.id for site in obj.sites.all()]
    
    def prepare_categories(self, obj):
        if obj.category:
            categories = [category.slug for category in obj.category.get_ancestors(ascending=False)]
            categories.append(obj.category.slug)
            return categories
    
    def prepare_thumbnail(self, obj):
        if obj.pictures.all():
            picture = obj.pictures.all()[0]
            return picture.thumbnail.url

    def prepare_profile(self, obj):
        if obj.pictures.all():
            picture = obj.pictures.all()[0]
            return picture.profile.url
    
    def prepare_owner_avatar(self, obj):
        if obj.owner.avatar:
            return obj.owner.thumbnail.url
        return ''

    def prepare_created_at_date(self, obj):
        return obj.created_at.date()

    def prepare_price(self, obj):
        # It doesn't play well with season
        if obj.prices.all():
            now = datetime.datetime.now()
            unit, amount = Booking.calculate_price(obj, now, now + datetime.timedelta(days=1))
        else:
            amount = None
        return amount
    
    def prepare_special(self, obj):
        try:
            obj.carproduct
            return True
        except ObjectDoesNotExist:
            pass

        try:
            obj.realestateproduct
            return True
        except ObjectDoesNotExist:
            pass

        return False

    def index_queryset(self):
        return Product.on_site.active()
        
class CarIndex(ProductIndex):

    brand = CharField(model_attr='brand')
    model = CharField(model_attr='model')

    # charactersitiques du vehicule
    seat_number = IntegerField(model_attr='seat_number')
    door_number = IntegerField(model_attr='door_number')
    fuel = IntegerField(model_attr='fuel')
    transmission = IntegerField(model_attr='transmission')
    mileage = IntegerField(model_attr='mileage')
    consumption = DecimalField(model_attr='consumption')

    # options & accessoires
    air_conditioning = BooleanField(model_attr='air_conditioning')
    power_steering = BooleanField(model_attr='power_steering')
    cruise_control = BooleanField(model_attr='cruise_control')
    gps = BooleanField(model_attr='gps')
    baby_seat = BooleanField(model_attr='baby_seat')
    roof_box = BooleanField(model_attr='roof_box')
    bike_rack = BooleanField(model_attr='bike_rack')
    snow_tires = BooleanField(model_attr='snow_tires')
    snow_chains = BooleanField(model_attr='snow_chains')
    ski_rack = BooleanField(model_attr='ski_rack')
    cd_player = BooleanField(model_attr='cd_player')
    audio_input = BooleanField(model_attr='audio_input')

    # informations de l'assurance
    tax_horsepower = DecimalField(model_attr='tax_horsepower')
    licence_plate = CharField(model_attr='licence_plate')
    first_registration_date = DateField(model_attr='first_registration_date')

    def index_queryset(self):
        return CarProduct.on_site.active()

class RealEstateIndex(ProductIndex):
    
    capacity = IntegerField(model_attr='capacity', null=True)
    private_life = IntegerField(model_attr='private_life', null=True)
    chamber_number = IntegerField(model_attr='chamber_number', null=True)
    rules = CharField(model_attr='rules', null=True)

    # services inclus
    air_conditioning = BooleanField(model_attr='air_conditioning')
    breakfast = BooleanField(model_attr='breakfast')
    balcony = BooleanField(model_attr='balcony')
    lockable_chamber = BooleanField(model_attr='lockable_chamber')
    towel = BooleanField(model_attr='towel')
    lift = BooleanField(model_attr='lift')
    family_friendly = BooleanField(model_attr='family_friendly')
    gym = BooleanField(model_attr='gym')
    accessible = BooleanField(model_attr='accessible')
    heating = BooleanField(model_attr='heating')
    jacuzzi = BooleanField(model_attr='jacuzzi')
    chimney = BooleanField(model_attr='chimney')
    internet_access = BooleanField(model_attr='internet_access')
    kitchen = BooleanField(model_attr='kitchen')
    parking = BooleanField(model_attr='parking')
    smoking_accepted = BooleanField(model_attr='smoking_accepted')
    ideal_for_events = BooleanField(model_attr='ideal_for_events')
    tv = BooleanField(model_attr='tv')
    washing_machine = BooleanField(model_attr='washing_machine')
    tumble_dryer = BooleanField(model_attr='tumble_dryer')
    computer_with_internet = BooleanField(model_attr='computer_with_internet')

    def index_queryset(self):
        return RealEstateProduct.on_site.active()

class AlertIndex(QueuedSearchIndex):
    designation = CharField(model_attr='designation')
    description = CharField(model_attr='description')
    created_at = DateTimeField(model_attr='created_at')
    patron = CharField(model_attr='patron__username', null=True)
    patron_url = CharField(model_attr='patron__get_absolute_url')
    lat = FloatField(model_attr='address__position__x', null=True)
    lng = FloatField(model_attr='address__position__y', null=True)
    text = CharField(document=True, use_template=True)
    sites = MultiValueField(faceted=True)
    url = CharField(model_attr='get_absolute_url', indexed=False)
    
    def prepare_sites(self, obj):
        return [site.id for site in obj.sites.all()]
    
    def index_queryset(self):
        return Alert.on_site.all()
    

try:
    site.register(Product, ProductIndex)
except AlreadyRegistered:
    pass

try:
    site.register(CarProduct, CarIndex)
except AlreadyRegistered:
    pass

try:
    site.register(RealEstateProduct, RealEstateIndex)
except AlreadyRegistered:
    pass

try:
    site.register(Alert, AlertIndex)
except AlreadyRegistered:
    pass


product_search = SearchQuerySet().models(Product).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)
product_only_search = SearchQuerySet().models(Product).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID).narrow('special:False')
car_search = SearchQuerySet().models(CarProduct).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)
realestate_search = SearchQuerySet().models(RealEstateProduct).facet('sites').facet('categories').facet('owner').facet('price').narrow('sites:%s' % settings.SITE_ID)
alert_search = SearchQuerySet().models(Alert)

