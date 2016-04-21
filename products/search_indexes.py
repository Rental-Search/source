#-*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

from django.core.mail import mail_admins
from django.template.loader import render_to_string

from haystack import indexes

from .models import Product
from .choices import UNIT
from .helpers import get_unavailable_periods

from haystack.utils.geo import ensure_point
from haystack.indexes import DeclarativeMetaclass
from django.utils.six import with_metaclass
from products.models import PropertyValue
from django.db.models import F

__all__ = ['ProductIndex']



class LocationMultiValueField(indexes.SearchField):
    """Handle multilocation"""
    field_type = 'location'

    def prepare(self, obj):
        return super(LocationMultiValueField, self).prepare(obj)

    def convert(self, value):
        if value:
            return list(value)
        else:
            return None


class AlgoliaLocationMultiValueField(LocationMultiValueField):
    field_type = 'location'
    
    index_fieldname = "_geoloc"
    


class AlgoliaTagsField(indexes.MultiValueField):
    
    index_fieldname = "_tags"
    
    def prepare(self, obj):
        
        category = obj._get_category()
        if category:
            qs = category.get_ancestors(ascending=False, include_self=True)
            return tuple(qs.values_list('slug', flat=True))
        
        return tuple()


class ProductPropertyFieldMixin(object):
    
    def __init__(self, *args, **kwargs):
        self.property_type = kwargs.pop('property_type')
        kwargs.update({'default':self.property_type.default, 
                        'faceted':self.property_type.faceted,
                        'null':True,})
        super(ProductPropertyFieldMixin, self).__init__(*args, **kwargs)
        self.index_fieldname = self.instance = \
                self.model_attr = self.property_type.attr_name 
        


class DynamicFieldsDeclarativeMetaClass(DeclarativeMetaclass):
    
    def __new__(cls, name, bases, attrs):
        clazz = DeclarativeMetaclass.__new__(cls, name, bases, attrs)
        if hasattr(clazz, '_get_dynamic_fields') \
                and hasattr(clazz, '_set_dynamic_fields'):
            clazz._fields = clazz.fields
            clazz.fields = property(fget=clazz._get_dynamic_fields, 
                          fset=clazz._set_dynamic_fields)
        return clazz
    

TYPE_FIELD_MAP = {'int':type('IntegerField', (ProductPropertyFieldMixin, indexes.IntegerField), {}),
                  'str':type('CharField', (ProductPropertyFieldMixin, indexes.CharField), {}),
                  'float':type('FloatField', (ProductPropertyFieldMixin, indexes.FloatField), {}),
                  'bool':type('BooleanField', (ProductPropertyFieldMixin, indexes.BooleanField), {}),
                  'choice':type('CharField', (ProductPropertyFieldMixin, indexes.CharField), {}),}


class ProductIndex(with_metaclass(DynamicFieldsDeclarativeMetaClass, 
                                  indexes.Indexable, indexes.SearchIndex)):
    
    text = indexes.CharField(document=True, use_template=True)
    location = indexes.LocationField(model_attr='address__position', null=True)
    locations = LocationMultiValueField()
    categories = indexes.MultiValueField(faceted=True, null=True)
    created_at = indexes.DateTimeField(model_attr='created_at')
    created_at_timestamp = indexes.DateTimeField(model_attr='created_at')
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
    vertical_profile = indexes.CharField(indexed=False, null=True)
    special = indexes.BooleanField()
    pro = indexes.BooleanField(model_attr='owner__is_professional', default=False)
    is_archived = indexes.BooleanField(model_attr='is_archived')
    is_allowed = indexes.BooleanField(model_attr='is_allowed')

    is_highlighted = indexes.BooleanField(default=False)#model_attr='is_highlighted')
    is_top = indexes.BooleanField(default=False)#model_attr='is_top')

    # introduced for UI 3 and API 2.0
    pro_owner = indexes.BooleanField(default=False)
    comment_count = indexes.IntegerField(model_attr='comment_count', default=0, indexed=False)
    average_rate = indexes.IntegerField(model_attr='average_rate', default=0, indexed=False)
    is_good = indexes.BooleanField(default=False)

    starts_unavailable = indexes.MultiValueField(faceted=True, null=True)
    ends_unavailable = indexes.MultiValueField(faceted=True, null=True)

    agencies = indexes.BooleanField(default=False)

    need_insurance = indexes.BooleanField(default=True)

    django_id_int = indexes.IntegerField(model_attr='id')
#     category_id = indexes.IntegerField(model_attr='category_id')
    algolia_categories = indexes.MultiValueField(faceted=True, null=True)
    _tags = AlgoliaTagsField(model_attr='categories', null=True)
    _geoloc = AlgoliaLocationMultiValueField()
    
    
    def __init__(self):
        super(ProductIndex, self).__init__()
        self._obj = None
    
    def _get_dynamic_fields(self):
        if hasattr(self, '_obj') and self._obj is not None:
            props = self._obj.fields_from_properties(TYPE_FIELD_MAP)
            fc = self._fields.copy()
            fc.update(props)
            return fc
        else:
            return self._fields
    
    def _set_dynamic_fields(self, obj):
        self._fields = obj
    
    def full_prepare(self, obj):
        self._obj = obj
        self._obj.annotate_with_property_values()
        return indexes.SearchIndex.full_prepare(self, self._obj)
            
    
    def get_updated_field(self):
        return "created_at"
    
    def prepare_locations(self, obj):
        agencies = obj.owner.pro_agencies.all()
        if agencies.count() > 0:
            positions = tuple([agency.position.x, agency.position.y] for agency in agencies if agency.position)
            return positions
        elif obj.address.position:
            return tuple([obj.address.position.x, obj.address.position.y])
        else:
            return None

    def prepare__geoloc(self, obj):
        locations = self.prepare_locations(obj)
        if locations:
            if isinstance(locations[0], list):
                return [{"lat":location[0], "lng":location[1]} for location in locations]
            else:
                return {"lat":locations[0], "lng":locations[1]}
        else:
            return None
    
    def prepare_need_insurance(self, obj):
        return obj.category.need_insurance
            

    def prepare_agencies(self, obj):
        if obj.owner.pro_agencies.all().count() > 0 :
            return True
        else:
            return False

    def prepare_sites(self, obj):
        return tuple(obj.sites.values_list('id', flat=True))
    
    def prepare_categories(self, obj):
        category = obj._get_category()
        if category:
            qs = category.get_ancestors(ascending=False, include_self=True)
            return tuple(qs.values_list('slug', flat=True))
    
    def prepare_algolia_categories(self, obj):
        category = obj._get_category()
        if category:
            cats = list(category\
                        .get_ancestors(ascending=False, include_self=True)\
                        .values_list('name', flat=True))
            
            cats_dict = {}
            for i in range(len(cats)):
                cats_dict['lvl'+str(i)] = " > ".join(cats[:i+1])
            
            return cats_dict
        
    def prepare_created_at_timestamp(self, obj):
        return (obj.created_at-datetime(1970,1,1)).total_seconds()
    
    def prepare_ends_unavailable(self, obj):
        started_at = datetime.now()
        starts, ends = get_unavailable_periods(obj, started_at)
        if len(ends): return tuple(ends)

    def prepare_starts_unavailable(self, obj):
        started_at = datetime.now()
        starts, ends = get_unavailable_periods(obj, started_at)
        if len(starts): return tuple(starts)

    def prepare_thumbnail(self, obj):
        for picture in obj.pictures.all()[:1]: # TODO: can we do this only once per product?
            return picture.thumbnail.url if picture.thumbnail else None

    def prepare_thumbnail_medium(self, obj):
        for picture in obj.pictures.all()[:1]: # TODO: can we do this only once per product?
            return picture.home.url if picture.home else None

    def prepare_profile(self, obj):
        for picture in obj.pictures.all()[:1]: # TODO: can we do this only once per product?
            return picture.profile.url if picture.profile else None

    def prepare_vertical_profile(self, obj):
        for picture in obj.pictures.all()[:1]: # TODO: can we do this only once per product?
            return picture.vertical_profile.url if picture.vertical_profile else None

    def prepare_owner_avatar(self, obj):
        obj = obj.owner
        return obj.thumbnail.url if obj.thumbnail else None

    def prepare_owner_avatar_medium(self, obj):
        obj = obj.owner
        return obj.product_page.url if obj.product_page else None

    def prepare_price(self, obj):
        prices = obj.prices.order_by('unit') # explicitly sort by 'unit'

        for price in prices:
            if price.unit >= UNIT.DAY:
                # either we have found the daily price, or there's no one
                break

        if prices:
            if price and price.unit == UNIT.DAY:
                return price.day_amount
            else:
                # there's no daily prices
                context = {'product': obj, }
                subject = render_to_string(
                        "products/emails/index_fail_email_subject.txt", context)
                text_message = render_to_string(
                        "products/emails/index_fail_email.txt", context)
                html_message = render_to_string(
                        "products/emails/index_fail_email.html", context)

                mail_admins(subject, text_message, html_message=html_message)

    def prepare_special(self, obj):
        special = hasattr(obj, 'carproduct') or hasattr(obj, 'realestateproduct')
        return special

    def prepare_pro_owner(self, obj):
        return obj.owner.current_subscription is not None

    def prepare_is_good(self, obj):
        # TODO: can we call prepare_thumbnail() only once per product?
        if obj.address and len(obj.description.split()) > 1 and self.prepare_thumbnail(obj):
            return True
        return False
#     
#     def prepare_category_id(self, obj):
#         return obj.category.id

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().on_site.select_related('category', 'address', 'owner')\
            .prefetch_related('category__properties', 'properties__property_type')
