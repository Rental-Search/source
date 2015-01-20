#-*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.utils.functional import memoize

from haystack import indexes

from products.models import Alert, Product, CarProduct, RealEstateProduct

__all__ = ['ProductIndex', 'AlertIndex']

ONE_DAY_DELTA = timedelta(days=1)

def cached_category(category_id, category):
    return tuple(category.get_ancestors(ascending=False, include_self=True).values_list('slug', flat=True))
_category = {}
cached_category = memoize(cached_category, _category, 1)

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
    is_archived = indexes.BooleanField(model_attr='is_archived')

    is_highlighted = indexes.BooleanField(default=False)#model_attr='is_highlighted')
    is_top = indexes.BooleanField(default=False)#model_attr='is_top')

    # introduced for UI 3 and API 2.0
    pro_owner = indexes.BooleanField(default=False, indexed=False)
    comment_count = indexes.IntegerField(model_attr='comment_count', default=0, indexed=False)
    average_rate = indexes.IntegerField(model_attr='average_rate', default=0, indexed=False)

    # summary field for checking product's description quality
    is_good = indexes.BooleanField(default=False, indexed=False)

    def prepare_sites(self, obj):
        return tuple(obj.sites.values_list('id', flat=True))
    
    def prepare_categories(self, obj):
        category = obj._get_category()
        if category:
            # it is safe to cache get_ancestors for categories and cache them by category PK
            return cached_category(category.pk, category)

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
        now = datetime.now()
        return obj.calculate_price(now, now + ONE_DAY_DELTA)[1]

    def prepare_special(self, obj):
        special = hasattr(obj, 'carproduct') or hasattr(obj, 'realestateproduct')
        return special

    def prepare_pro_owner(self, obj):
        return obj.owner.current_subscription is not None

    def prepare_is_good(self, obj):
        return True if len(obj.description.split()) > 1 else False

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().on_site.active().select_related('category', 'address', 'owner')


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
    air_conditioning = indexes.BooleanField(model_attr='air_conditioning', null=True)
    power_steering = indexes.BooleanField(model_attr='power_steering', null=True)
    cruise_control = indexes.BooleanField(model_attr='cruise_control', null=True)
    gps = indexes.BooleanField(model_attr='gps', null=True)
    baby_seat = indexes.BooleanField(model_attr='baby_seat', null=True)
    roof_box = indexes.BooleanField(model_attr='roof_box', null=True)
    bike_rack = indexes.BooleanField(model_attr='bike_rack', null=True)
    snow_tires = indexes.BooleanField(model_attr='snow_tires', null=True)
    snow_chains = indexes.BooleanField(model_attr='snow_chains', null=True)
    ski_rack = indexes.BooleanField(model_attr='ski_rack', null=True)
    cd_player = indexes.BooleanField(model_attr='cd_player', null=True)
    audio_input = indexes.BooleanField(model_attr='audio_input', null=True)

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
    air_conditioning = indexes.BooleanField(model_attr='air_conditioning', null=True)
    breakfast = indexes.BooleanField(model_attr='breakfast', null=True)
    balcony = indexes.BooleanField(model_attr='balcony', null=True)
    lockable_chamber = indexes.BooleanField(model_attr='lockable_chamber', null=True)
    towel = indexes.BooleanField(model_attr='towel', null=True)
    lift = indexes.BooleanField(model_attr='lift', null=True)
    family_friendly = indexes.BooleanField(model_attr='family_friendly', null=True)
    gym = indexes.BooleanField(model_attr='gym', null=True)
    accessible = indexes.BooleanField(model_attr='accessible', null=True)
    heating = indexes.BooleanField(model_attr='heating', null=True)
    jacuzzi = indexes.BooleanField(model_attr='jacuzzi', null=True)
    chimney = indexes.BooleanField(model_attr='chimney', null=True)
    internet_access = indexes.BooleanField(model_attr='internet_access', null=True)
    kitchen = indexes.BooleanField(model_attr='kitchen', null=True)
    parking = indexes.BooleanField(model_attr='parking', null=True)
    smoking_accepted = indexes.BooleanField(model_attr='smoking_accepted', null=True)
    ideal_for_events = indexes.BooleanField(model_attr='ideal_for_events')
    tv = indexes.BooleanField(model_attr='tv', null=True)
    washing_machine = indexes.BooleanField(model_attr='washing_machine', null=True)
    tumble_dryer = indexes.BooleanField(model_attr='tumble_dryer', null=True)
    computer_with_internet = indexes.BooleanField(model_attr='computer_with_internet', null=True)

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
        return tuple(obj.sites.values_list('id', flat=True))

    def get_model(self):
        return Alert

    def index_queryset(self, using=None):
        return self.get_model().on_site.select_related('address', 'patron')
