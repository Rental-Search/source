# -*- coding: utf-8 -*-

from itertools import chain

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.urlresolvers import NoReverseMatch
from rest_framework.fields import (
        FloatField, DateTimeField,
        IntegerField, DecimalField,
        CharField, SerializerMethodField,
)
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.reverse import reverse
from rest_framework import serializers

from products import models
from accounts.serializers import NestedAddressSerializer, BooleanField, NestedUserSerializer
from eloue.api.serializers import (
    EncodedImageField, ObjectMethodBooleanField, ModelSerializer,
    NestedModelSerializerMixin, SimpleSerializer, SimplePaginationSerializer
)
from eloue.decorators import cached
from products.helpers import calculate_available_quantity
from products.choices import PRODUCT_TYPE

from rent.utils import DATE_TIME_FORMAT
from rent.models import Booking
from rent.choices import BOOKING_STATE


def category_cache_key(*args):
    return u':'.join([
        str(item.id if isinstance(item, models.Category) else item)
            for item in chain(args, PRODUCT_TYPE.values())
        ])


@cached(key_func=category_cache_key, timeout=15*60)
def get_root_category(category):
    return category.get_root().id


class CategorySerializer(ModelSerializer):
    is_child_node = ObjectMethodBooleanField('is_child_node', read_only=True)
    is_leaf_node = ObjectMethodBooleanField('is_leaf_node', read_only=True)
    is_root_node = ObjectMethodBooleanField('is_root_node', read_only=True)

    class Meta:
        model = models.Category
        fields = ('id', 'parent', 'name', 'need_insurance', 'slug',
                  'title', 'description', 'header', 'footer',
                  'is_child_node', 'is_leaf_node', 'is_root_node')
        public_fields = (
            'id', 'parent', 'name', 'need_insurance', 'slug',
            'title', 'description', 'header', 'footer',
            'is_child_node', 'is_leaf_node', 'is_root_node')
        read_only_fields = ('slug',)
        immutable_fields = ('parent',)

class NestedCategorySerializer(NestedModelSerializerMixin, CategorySerializer):
    pass

class PriceSerializer(ModelSerializer):
    # FIXME: uncomment if we need to provide 'local_currency_amount' instead of 'amount' to clients, remove otherwise
    def _transform_amount(self, obj, value):
        return self.fields['amount'].field_to_native(obj, 'local_currency_amount')

    class Meta:
        model = models.Price
        fields = ('id', 'product', 'name', 'amount', 'currency', 'unit')
        public_fields = ('id', 'product', 'name', 'amount', 'currency', 'unit')
        immutable_fields = ('product', 'currency')

class NestedPriceSerializer(NestedModelSerializerMixin, PriceSerializer):
    pass

class PictureSerializer(ModelSerializer):
    image = EncodedImageField(('thumbnail', 'profile', 'home', 'display'))

    class Meta:
        model = models.Picture
        fields = ('id', 'product', 'image', 'created_at')
        public_fields = ('id', 'product', 'image', 'created_at')
        read_only_fields = ('created_at',)
        immutable_fields = ('product',)

class NestedPictureSerializer(NestedModelSerializerMixin, PictureSerializer):
    pass

class RequiredBooleanField(BooleanField):
    def __init__(self, required=None, **kwargs):
        return super(RequiredBooleanField, self).__init__(required=True, **kwargs)

def map_require_boolean_field(field_mapping):
    from django.db.models import BooleanField as ModelBooleanField
    field_mapping[ModelBooleanField] = RequiredBooleanField
    return field_mapping

class RequiredBooleanFieldSerializerMixin(object):
    field_mapping = map_require_boolean_field(ModelSerializer.field_mapping)

class ProductSerializer(ModelSerializer):
    address = NestedAddressSerializer()
    average_note = FloatField(read_only=True)
    comment_count = IntegerField(read_only=True)
    category = NestedCategorySerializer()
    prices = NestedPriceSerializer(read_only=True, many=True)
    pictures = NestedPictureSerializer(read_only=True, many=True)
    owner = NestedUserSerializer()
    slug = CharField(read_only=True, source='slug')


    def validate(self, attrs):
        attrs = super(ProductSerializer, self).validate(attrs)

        # update existing project
        if self.object is not None:
            old_category = self.object._get_category()
            new_category = attrs.get('category', None)

            ext_categories = set(PRODUCT_TYPE.values())

            # If categories are belong to different trees, we have to check
            # possibility to change category
            if old_category.tree_id != new_category.tree_id:
                if get_root_category(old_category) in ext_categories or \
                        get_root_category(new_category) in ext_categories:
                    raise serializers.ValidationError(
                        _(u'Vous ne pouvez pas modifier la catégorie'))

        return attrs

    def full_clean(self, instance):
        instance = super(ProductSerializer, self).full_clean(instance)
        if instance and instance.deposit_amount < 0:
            self._errors.update({
                'deposit_amount': _(u'Value can\'t be negative')
            })
            return None
        return instance

    def to_native(self, obj):
        try:
            obj.category = obj._get_category()
        except AttributeError:
            pass
        return super(ProductSerializer, self).to_native(obj)

    class Meta:
        model = models.Product
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'average_note', 'prices',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies', 'comment_count',
                  'pictures', 'slug')
        public_fields = (
            'id', 'summary', 'deposit_amount', 'currency', 'description',
            'address', 'quantity', 'category', 'owner',  'comment_count',
            'pro_agencies', 'prices', 'pictures', 'average_note', 'slug')
        view_name = 'product-detail'
        read_only_fields = ('is_archived', 'created_at')
        immutable_fields = ('owner',)

class NestedProductSerializer(NestedModelSerializerMixin, ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.public_fields

class CarProductSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        model = models.CarProduct
        fields = ProductSerializer.Meta.fields + (
            # CarProduct extended fields
            'brand', 'model', 'seat_number', 'door_number', 'fuel', 'transmission', 'mileage',
            'consumption', 'km_included', 'costs_per_km', 'air_conditioning', 'power_steering',
            'cruise_control', 'gps', 'baby_seat', 'roof_box', 'bike_rack', 'snow_tires', 'snow_chains',
            'ski_rack', 'cd_player', 'audio_input', 'tax_horsepower', 'licence_plate', 'first_registration_date',
        )
        public_fields = ProductSerializer.Meta.public_fields + (
            'brand', 'model', 'seat_number', 'door_number', 'fuel',
            'transmission', 'mileage', 'consumption', 'km_included',
            'costs_per_km', 'air_conditioning', 'power_steering',
            'cruise_control', 'gps', 'baby_seat', 'roof_box', 'bike_rack',
            'snow_tires', 'snow_chains', 'ski_rack', 'cd_player',
            'audio_input', 'tax_horsepower', 'licence_plate',
            'first_registration_date',
        )

class RealEstateProductSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        model = models.RealEstateProduct
        fields = ProductSerializer.Meta.fields + (
            # RealEstateProduct extended fields
            'capacity', 'private_life', 'chamber_number', 'rules', 'air_conditioning', 'breakfast', 'balcony',
            'lockable_chamber', 'towel', 'lift', 'family_friendly', 'gym', 'accessible', 'heating', 'jacuzzi',
            'chimney', 'internet_access', 'kitchen', 'parking', 'smoking_accepted', 'ideal_for_events', 'tv',
            'washing_machine', 'tumble_dryer', 'computer_with_internet',
        )
        public_fields = ProductSerializer.Meta.public_fields + (
            'capacity', 'private_life', 'chamber_number', 'rules',
            'air_conditioning', 'breakfast', 'balcony', 'lockable_chamber',
            'towel', 'lift', 'family_friendly', 'gym', 'accessible',
            'heating', 'jacuzzi', 'chimney', 'internet_access', 'kitchen',
            'parking', 'smoking_accepted', 'ideal_for_events', 'tv',
            'washing_machine', 'tumble_dryer', 'computer_with_internet',
        )

class CuriositySerializer(ModelSerializer):
    class Meta:
        model = models.Curiosity
        fields = ('id', 'product')
        public_fields = ('id', 'product')
        immutable_fields = ('product',)

class ProductRelatedMessageSerializer(ModelSerializer):
    class Meta:
        model = models.ProductRelatedMessage
        fields = ('id', 'thread', 'sender', 'recipient', 'body', 'sent_at', 'read_at', 'replied_at', 'offer')
        read_only_fields = ('sent_at',)
        immutable_fields = ('thread', 'sender', 'recipient', 'offer')

class NestedProductRelatedMessageSerializer(NestedModelSerializerMixin, ProductRelatedMessageSerializer):
    pass

class MessageThreadSerializer(ModelSerializer):
    sender = NestedUserSerializer()
    recipient = NestedUserSerializer()
    last_message = NestedProductRelatedMessageSerializer(read_only=True)
    seen = BooleanField(read_only=True)

    class Meta:
        model = models.MessageThread
        fields = ('id', 'sender', 'recipient', 'product', 'last_message',
                'subject', 'sender_archived', 'recipient_archived', 'messages',
                'seen')
        read_only_fields = ('sender_archived', 'recipient_archived', 'messages')
        immutable_fields = ('sender', 'recipient', 'product')

class ShippingPriceParamsSerializer(SimpleSerializer):
    arrival_point_id = IntegerField(required=True)


class ShippingPriceSerializer(SimpleSerializer):
    price = DecimalField(required=True, decimal_places=2, max_digits=10)
    token = CharField(required=True)


class UnavailabilityPeriodSerializer(ModelSerializer):

    def full_clean(self, instance):
        instance = super(UnavailabilityPeriodSerializer, self).full_clean(instance)
        if instance and instance.quantity > calculate_available_quantity(instance.product, instance.started_at, instance.ended_at):
            self._errors.update({
                'quantity': _(u'You can\'t make unavailable such quantity.')
            })
            return None
        return instance

    class Meta:
        model = models.UnavailabilityPeriod
        fields = ('id', 'product', 'quantity', 'started_at', 'ended_at',)
        public_fields = ('id', 'product', 'quantity', 'started_at', 'ended_at',)
        immutable_fields = ('product',)


class UnavailabilityPeriodSerializerMixin(object):
    def _filter_periods(self, qs, attrs):
        filter_kwargs = {
            'product': self.product,
            'ended_at__gt': attrs.get('started_at'),
            'started_at__lt': attrs.get('ended_at')
        }

        return qs.filter(**filter_kwargs).only(
            'pk', 'quantity', 'started_at', 'ended_at', 'product__id'
        )

    def validate(self, attrs):
        attrs = super(UnavailabilityPeriodSerializerMixin, self).validate(attrs)

        started_at = attrs.get('started_at')
        ended_at = attrs.get('ended_at')

        if started_at >= ended_at:
            raise ValidationError(_(u"Une location ne peut pas terminer avant d'avoir commencer"))

        return attrs


class NestedUnavailabilityPeriodSerializer(UnavailabilityPeriodSerializer):
    class Meta:
        model = models.UnavailabilityPeriod
        fields = ('id', 'quantity', 'started_at', 'ended_at',)
        public_fields = ('id', 'quantity', 'started_at', 'ended_at',)


class NestedBookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = ('quantity', 'started_at', 'ended_at',)
        public_fields = ('quantity', 'started_at', 'ended_at',)


BOOKED_STATE = (
    BOOKING_STATE.PENDING,
    BOOKING_STATE.ONGOING,
)


class ListUnavailabilityPeriodSerializer(UnavailabilityPeriodSerializerMixin, SimpleSerializer):
    started_at = DateTimeField(write_only=True, input_formats=DATE_TIME_FORMAT)
    ended_at = DateTimeField(write_only=True, input_formats=DATE_TIME_FORMAT)
    unavailable_periods = SerializerMethodField('get_unavailable_periods')
    booking_periods = SerializerMethodField('get_booking_periods')

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('instance')
        super(ListUnavailabilityPeriodSerializer, self).__init__(*args, **kwargs)

    def get_booking_periods(self, attrs):
        qs = Booking.objects.filter(state__in=BOOKED_STATE)
        serializer = NestedBookingSerializer(
            instance=self._filter_periods(qs, attrs),
            many=True)
        return serializer.data

    def get_unavailable_periods(self, attrs):
        qs = models.UnavailabilityPeriod.objects.all()
        serializer = NestedUnavailabilityPeriodSerializer(
            instance=self._filter_periods(qs, attrs),
            many=True)
        return serializer.data


class OptionalIntegerField(IntegerField):
    def field_to_native(self, obj, field_name):
        try:
            return super(OptionalIntegerField, self).field_to_native(obj, field_name)
        except AttributeError:
            pass


class HyperlinkedByIdField(HyperlinkedIdentityField):
    def __init__(self, *args, **kwargs):
        try:
            self.source = kwargs.get('source')
        except KeyError:
            msg = _("HyperlinkedByIdField requires 'source' argument")
            raise ValueError(msg)
        return super(HyperlinkedByIdField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        source = getattr(obj, self.source, None)

        try:
            return reverse(view_name, [source, ], request=request, format=format)
        except NoReverseMatch:
            return super(HyperlinkedByIdField, self).get_url(obj, view_name, request, format)


class MixUnavailabilityPeriodSerializer(UnavailabilityPeriodSerializerMixin, SimpleSerializer):
    id = OptionalIntegerField(read_only=True, required=False)
    product = HyperlinkedByIdField(source='product_id',
        view_name='product-detail')
    quantity = IntegerField(read_only=True)
    started_at = DateTimeField(input_formats=DATE_TIME_FORMAT)
    ended_at = DateTimeField(input_formats=DATE_TIME_FORMAT)

    def __init__(self, *args, **kwargs):
        self.product = kwargs['context']['product']
        super(MixUnavailabilityPeriodSerializer, self).__init__(*args, **kwargs)

    @property
    def data(self):
        self.object = self.context['object']
        return super(MixUnavailabilityPeriodSerializer, self).data

    @property
    def errors(self):
        _errors = super(MixUnavailabilityPeriodSerializer, self).errors
        if _errors and isinstance(_errors, (list, tuple)):
            self._errors = _errors[0]
        return self._errors

    def restore_object(self, attrs, instance=None):
        bookings = Booking.objects.filter(state__in=BOOKED_STATE)
        unavailability_periods = models.UnavailabilityPeriod.objects.all()

        self.context['object'] = list(chain(*tuple([
            tuple(self._filter_periods(qs, attrs))
            for qs in (bookings, unavailability_periods)
        ])))

        return super(MixUnavailabilityPeriodSerializer, self).restore_object(attrs, instance=instance)


class MixUnavailabilityPeriodPaginatedSerializer(SimplePaginationSerializer):
    class Meta:
        object_serializer_class = MixUnavailabilityPeriodSerializer
