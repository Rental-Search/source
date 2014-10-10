#-*- coding: utf-8 -*-
import datetime

from haystack import indexes

from products.models import Alert, Product, CarProduct, RealEstateProduct

__all__ = ['ProductIndex', 'AlertIndex']

ONE_DAY_DELTA = datetime.timedelta(days=1)

class ProductIndex(indexes.Indexable, indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    location = indexes.LocationField(model_attr='address__position', null=True)

    categories = indexes.MultiValueField(faceted=True, null=True)
    created_at = indexes.DateTimeField(model_attr='created_at')
    created_at_date = indexes.DateField(model_attr='created_at__date')
    description = indexes.EdgeNgramField(model_attr='description')
    city = indexes.CharField(model_attr='address__city', indexed=False)
    zipcode = indexes.CharField(model_attr='address__zipcode', indexed=False)
    owner = indexes.CharField(model_attr='owner__username', faceted=True)
    owner_url = indexes.CharField(model_attr='owner__get_absolute_url', indexed=False)
    owner_avatar = indexes.CharField(null=True)
    owner_avatar_medium = indexes.CharField(null=True)
    price = indexes.FloatField(faceted=True, null=True)
    sites = indexes.MultiValueField(faceted=True)
    summary = indexes.EdgeNgramField(model_attr='summary')
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)
    thumbnail = indexes.CharField(indexed=False, null=True)
    thumbnail_medium = indexes.CharField(indexed=False, null=True)
    profile = indexes.CharField(indexed=False, null=True)
    special = indexes.BooleanField()
    pro = indexes.BooleanField(model_attr='owner__is_professional', default=False)
    pro_owner = indexes.BooleanField(default=False)
    
    is_highlighted = indexes.BooleanField(model_attr='is_highlighted')
    is_top = indexes.BooleanField(model_attr='is_top')

    
    def prepare_sites(self, obj):
        return tuple(obj.sites.values_list('id', flat=True))
    
    def prepare_categories(self, obj):
        if obj.category:
            return [category.slug for category in obj.category.get_ancestors(ascending=False, include_self=True)]

    def prepare_thumbnail(self, obj):
        for picture in obj.pictures.all()[:1]:
            return picture.thumbnail.url if picture.thumbnail else None

    def prepare_thumbnail_medium(self, obj):
        for picture in obj.pictures.all()[:1]:
            return picture.home.url if picture.home else None

    def prepare_profile(self, obj):
        for picture in obj.pictures.all()[:1]:
            return picture.profile.url if picture.profile else None

    def prepare_owner_avatar(self, obj):
        obj = obj.owner
        return obj.thumbnail.url if obj.thumbnail else None

    def prepare_owner_avatar_medium(self, obj):
        obj = obj.owner
        return obj.product_page.url if obj.product_page else None

    def prepare_price(self, obj):
        # It doesn't play well with season
        if obj.prices.all()[:1]:
            now = datetime.datetime.now()
            unit, amount = obj.calculate_price(now, now + ONE_DAY_DELTA)
            return amount
    
    def prepare_special(self, obj):
        special = hasattr(obj, 'carproduct') or hasattr(obj, 'realestateproduct')
        return special

    def prepare_pro_owner(self, obj):
        return obj.owner.current_subscription is not None

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().on_site.active().select_related('address', 'owner')#.prefetch_related('pictures', 'prices')
        
class CarIndex(ProductIndex):

    brand = indexes.CharField(model_attr='brand')
    model = indexes.CharField(model_attr='model')

    # charactersitiques du vehicule
    seat_number = indexes.IntegerField(model_attr='seat_number')
    door_number = indexes.IntegerField(model_attr='door_number')
    fuel = indexes.IntegerField(model_attr='fuel')
    transmission = indexes.IntegerField(model_attr='transmission')
    mileage = indexes.IntegerField(model_attr='mileage')
    consumption = indexes.DecimalField(model_attr='consumption')

    # options & accessoires
    air_conditioning = indexes.BooleanField(model_attr='air_conditioning')
    power_steering = indexes.BooleanField(model_attr='power_steering')
    cruise_control = indexes.BooleanField(model_attr='cruise_control')
    gps = indexes.BooleanField(model_attr='gps')
    baby_seat = indexes.BooleanField(model_attr='baby_seat')
    roof_box = indexes.BooleanField(model_attr='roof_box')
    bike_rack = indexes.BooleanField(model_attr='bike_rack')
    snow_tires = indexes.BooleanField(model_attr='snow_tires')
    snow_chains = indexes.BooleanField(model_attr='snow_chains')
    ski_rack = indexes.BooleanField(model_attr='ski_rack')
    cd_player = indexes.BooleanField(model_attr='cd_player')
    audio_input = indexes.BooleanField(model_attr='audio_input')

    # informations de l'assurance
    tax_horsepower = indexes.DecimalField(model_attr='tax_horsepower')
    licence_plate = indexes.CharField(model_attr='licence_plate')
    first_registration_date = indexes.DateField(model_attr='first_registration_date')

    def get_model(self):
        return CarProduct

class RealEstateIndex(ProductIndex):
    
    capacity = indexes.IntegerField(model_attr='capacity', null=True)
    private_life = indexes.IntegerField(model_attr='private_life', null=True)
    chamber_number = indexes.IntegerField(model_attr='chamber_number', null=True)
    rules = indexes.CharField(model_attr='rules', null=True)

    # services inclus
    air_conditioning = indexes.BooleanField(model_attr='air_conditioning')
    breakfast = indexes.BooleanField(model_attr='breakfast')
    balcony = indexes.BooleanField(model_attr='balcony')
    lockable_chamber = indexes.BooleanField(model_attr='lockable_chamber')
    towel = indexes.BooleanField(model_attr='towel')
    lift = indexes.BooleanField(model_attr='lift')
    family_friendly = indexes.BooleanField(model_attr='family_friendly')
    gym = indexes.BooleanField(model_attr='gym')
    accessible = indexes.BooleanField(model_attr='accessible')
    heating = indexes.BooleanField(model_attr='heating')
    jacuzzi = indexes.BooleanField(model_attr='jacuzzi')
    chimney = indexes.BooleanField(model_attr='chimney')
    internet_access = indexes.BooleanField(model_attr='internet_access')
    kitchen = indexes.BooleanField(model_attr='kitchen')
    parking = indexes.BooleanField(model_attr='parking')
    smoking_accepted = indexes.BooleanField(model_attr='smoking_accepted')
    ideal_for_events = indexes.BooleanField(model_attr='ideal_for_events')
    tv = indexes.BooleanField(model_attr='tv')
    washing_machine = indexes.BooleanField(model_attr='washing_machine')
    tumble_dryer = indexes.BooleanField(model_attr='tumble_dryer')
    computer_with_internet = indexes.BooleanField(model_attr='computer_with_internet')

    def get_model(self):
        return RealEstateProduct

class AlertIndex(indexes.Indexable, indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    location = indexes.LocationField(model_attr='address__position', null=True)

    designation = indexes.CharField(model_attr='designation')
    description = indexes.CharField(model_attr='description')
    created_at = indexes.DateTimeField(model_attr='created_at')
    patron = indexes.CharField(model_attr='patron__username', null=True)
    patron_url = indexes.CharField(model_attr='patron__get_absolute_url')
    sites = indexes.MultiValueField(faceted=True)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)
    
    def prepare_sites(self, obj):
        res = obj.sites.all().values_list('id', flat=True)
        return tuple(res)

    def get_model(self):
        return Alert

    def index_queryset(self, using=None):
        return self.get_model().on_site.select_related('address', 'patron')
