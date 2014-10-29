# -*- coding: utf-8 -*-
from rest_framework.fields import FloatField, IntegerField
from rest_framework.fields import CharField
from products import models
from accounts.serializers import NestedAddressSerializer, ProductNestedPhoneNumberSerializer, BooleanField, NestedUserSerializer
from eloue.api.serializers import EncodedImageField, ObjectMethodBooleanField, ModelSerializer, \
    NestedModelSerializerMixin


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
    phone = ProductNestedPhoneNumberSerializer()

    class Meta:
        model = models.Product
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'average_note', 'prices',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies', 'comment_count',
                  'pictures', 'slug', 'phone')
        public_fields = (
            'id', 'summary', 'deposit_amount', 'currency', 'description', 'phone',
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

class MessageThreadSerializer(ModelSerializer):
    class Meta:
        model = models.MessageThread
        fields = ('id', 'sender', 'recipient', 'product', 'last_message', 'subject', 'sender_archived', 'recipient_archived', 'messages')
        read_only_fields = ('last_message', 'sender_archived', 'recipient_archived', 'messages')
        immutable_fields = ('sender', 'recipient', 'product')

class ProductRelatedMessageSerializer(ModelSerializer):
    class Meta:
        model = models.ProductRelatedMessage
        fields = ('id', 'thread', 'sender', 'recipient', 'body', 'sent_at', 'read_at', 'replied_at', 'offer')
        read_only_fields = ('sent_at',)
        immutable_fields = ('thread', 'sender', 'recipient', 'offer')
