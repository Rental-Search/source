# -*- coding: utf-8 -*-
from products import models
from accounts.serializers import NestedAddressSerializer, NestedPhoneNumberSerializer, BooleanField
from eloue.api.serializers import EncodedImageField, ObjectMethodBooleanField, ModelSerializer


class CategorySerializer(ModelSerializer):
    is_child_node = ObjectMethodBooleanField('is_child_node', read_only=True)
    is_leaf_node = ObjectMethodBooleanField('is_leaf_node', read_only=True)
    is_root_node = ObjectMethodBooleanField('is_root_node', read_only=True)

    class Meta:
        model = models.Category
        fields = ('id', 'parent', 'name', 'need_insurance',
                  'title', 'description', 'header', 'footer',
                  'is_child_node', 'is_leaf_node', 'is_root_node')
        public_fields = (
            'id', 'parent', 'name', 'need_insurance',
            'title', 'description', 'header', 'footer',
            'is_child_node', 'is_leaf_node', 'is_root_node')
        immutable_fields = ('parent',)

class RequiredBooleanField(BooleanField):
    def __init__(self, required=None, **kwargs):
        return super(RequiredBooleanField, self).__init__(required=True, **kwargs)

def map_require_boolean_field(field_mapping):
    from django.db.models import BooleanField as ModelBooleanField
    field_mapping[ModelBooleanField] = RequiredBooleanField
    return field_mapping

class RequiredBooleanFieldSerializerMixin(object):
    field_mapping = map_require_boolean_field(ModelSerializer.field_mapping)

class ProductSerializer(RequiredBooleanFieldSerializerMixin, ModelSerializer):
    address = NestedAddressSerializer()
    phone = NestedPhoneNumberSerializer(required=False)

    class Meta:
        model = models.Product
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'phone',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies')
        public_fields = (
            'id', 'summary', 'deposit_amount', 'currency', 'description',
            'address', 'phone', 'quantity', 'category', 'owner',
            'pro_agencies')
        view_name = 'product-detail'
        read_only_fields = ('is_archived', 'created_at')
        immutable_fields = ('owner',)

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

class PriceSerializer(ModelSerializer):
    # FIXME: uncomment if we need to provide 'local_currency_amount' instead of 'amount' to clients, remove otherwise
    def _transform_amount(self, obj, value):
        return self.fields['amount'].field_to_native(obj, 'local_currency_amount')

    class Meta:
        model = models.Price
        fields = ('id', 'product', 'name', 'amount', 'currency', 'unit')
        public_fields = ('id', 'product', 'name', 'amount', 'currency', 'unit')
        immutable_fields = ('product', 'currency')

class PictureSerializer(ModelSerializer):
    image = EncodedImageField(('thumbnail', 'profile', 'home', 'display'))

    class Meta:
        model = models.Picture
        fields = ('id', 'product', 'image', 'created_at')
        public_fields = ('id', 'product', 'image', 'created_at')
        read_only_fields = ('created_at',)
        immutable_fields = ('product',)

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
        fields = ('id', 'thread', 'sender', 'recipient', 'body', 'sent_at', 'offer')
        read_only_fields = ('sent_at',)
        immutable_fields = ('thread', 'sender', 'recipient', 'offer')
