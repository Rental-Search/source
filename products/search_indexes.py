#-*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

from django.core.mail import mail_admins
from django.template.loader import render_to_string

from haystack import indexes

from .models import Product
from .choices import UNIT
from .helpers import get_unavailable_periods

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


class AlgoliaLocationField(indexes.LocationField):
    field_type = 'location'
    
    index_fieldname = "_geoloc"
    
    def prepare(self, obj):
        from haystack.utils.geo import ensure_point

        value = super(indexes.LocationField, self).prepare(obj)

        if value is None:
            return None

        pnt = ensure_point(value)
        pnt_lat, pnt_lng  = pnt.get_coords()
        return {"lat":pnt_lat, "lng":pnt_lng}


class AlgoliaTagsField(indexes.MultiValueField):
    
    index_fieldname = "_tags"
    
    def prepare(self, obj):
        
        category = obj._get_category()
        if category:
            qs = category.get_ancestors(ascending=False, include_self=True)
            return tuple(qs.values_list('slug', flat=True))
        
        return tuple()
            

class ProductIndex(indexes.Indexable, indexes.SearchIndex):
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
    algolia_categories = indexes.MultiValueField(faceted=True, null=True)
    _geoloc = AlgoliaLocationField(model_attr='address__position', null=True)
    _tags = AlgoliaTagsField(model_attr='categories', null=True)
    
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

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().on_site.select_related('category', 'address', 'owner')
