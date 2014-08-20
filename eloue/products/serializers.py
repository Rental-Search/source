
from rest_framework.serializers import HyperlinkedModelSerializer, BooleanField
from rest_framework import fields

from products import models
from products.choices import UNIT
from eloue.api.serializers import EncodedImageField

class CategoryDescriptionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.CategoryDescription
        fields = ('title', 'description', 'header', 'footer')

class CategorySerializer(HyperlinkedModelSerializer):
    description = CategoryDescriptionSerializer()
    is_child_node = BooleanField(read_only=True)
    is_leaf_node = BooleanField(read_only=True)
    is_root_node = BooleanField(read_only=True)

    def transform_is_child_node(self, obj, value):
        return bool(obj and obj.is_child_node())

    def transform_is_leaf_node(self, obj, value):
        return bool(obj and obj.is_leaf_node())

    def transform_is_root_node(self, obj, value):
        return bool(obj and obj.is_root_node())

    class Meta:
        model = models.Category
        fields = ('id', 'parent', 'name', 'need_insurance', 'description', 'is_child_node', 'is_leaf_node', 'is_root_node')
        read_only_fields = ('id', 'parent')

class ProductSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'phone',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies')
        read_only_fields = ('id', 'owner', 'address', 'phone', 'quantity')

class CarProductSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.CarProduct
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'phone',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies',
                  # CarProduct extended fields
                  'brand', 'model', 'seat_number', 'door_number', 'fuel', 'transmission', 'mileage',
                  'consumption', 'km_included', 'costs_per_km', 'air_conditioning', 'power_steering',
                  'cruise_control', 'gps', 'baby_seat', 'roof_box', 'bike_rack', 'snow_tires', 'snow_chains',
                  'ski_rack', 'cd_player', 'audio_input', 'tax_horsepower', 'licence_plate', 'first_registration_date')
        read_only_fields = ('id', 'owner', 'address', 'phone', 'quantity')
        view_name = 'product-detail'

class RealEstateProductSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.RealEstateProduct
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'phone',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies',
                  # RealEstateProduct extended fields
                  'capacity', 'private_life', 'chamber_number', 'rules', 'air_conditioning', 'breakfast', 'balcony',
                  'lockable_chamber', 'towel', 'lift', 'family_friendly', 'gym', 'accessible', 'heating', 'jacuzzi',
                  'chimney', 'internet_access', 'kitchen', 'smoking_accepted', 'ideal_for_events', 'tv',
                  'washing_machine', 'tumble_dryer', 'computer_with_internet')
        read_only_fields = ('id', 'owner', 'address', 'phone', 'quantity')
        view_name = 'product-detail'

class PriceSerializer(HyperlinkedModelSerializer):
    amount = fields.DecimalField(source='local_currency_amount', max_digits=10, decimal_places=2)

    def transform_currency(self, obj, value):
        return value and {
            'id': value,
            'symbol': obj.get_currency_display(),
        }

    def transform_unit(self, obj, value):
        return value and {
            'id': value,
            'name': UNIT[value][1],
        }

    class Meta:
        model = models.Price
        fields = ('id', 'product', 'name', 'amount', 'currency', 'unit')
        read_only_fields = ('id', 'product')

class PictureSerializer(HyperlinkedModelSerializer):
    image = EncodedImageField()

    def transform_image(self, obj, value):
        image = {
            k: getattr(obj, k).url if value else ''
            for k in ('thumbnail', 'profile', 'home', 'display')
        }
        return image

    class Meta:
        model = models.Picture
        fields = ('id', 'product', 'image', 'created_at')
        read_only_fields = ('id', 'created_at')

class CuriositySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Curiosity
        fields = ('id', 'product')

class MessageThreadSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.MessageThread
        fields = ('id', 'sender', 'recipient', 'product', 'last_message', 'subject', 'sender_archived', 'recipient_archived', 'messages')
        read_only_fields = ('id', 'last_message', 'messages', 'sender')

class ProductRelatedMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.ProductRelatedMessage
        fields = ('id', 'thread', 'sender', 'recipient', 'body', 'sent_at', 'offer')
        read_only_fields = ('id', 'sent_at', 'sender')
