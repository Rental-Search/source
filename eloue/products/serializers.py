
from rest_framework import fields

from products import models
from eloue.api.serializers import EncodedImageField, ObjectMethodBooleanField, ModelSerializer

class CategoryDescriptionSerializer(ModelSerializer):
    class Meta:
        model = models.CategoryDescription
        fields = ('title', 'description', 'header', 'footer')

class CategorySerializer(ModelSerializer):
    description = CategoryDescriptionSerializer()
    is_child_node = ObjectMethodBooleanField('is_child_node', read_only=True)
    is_leaf_node = ObjectMethodBooleanField('is_leaf_node', read_only=True)
    is_root_node = ObjectMethodBooleanField('is_root_node', read_only=True)

    class Meta:
        model = models.Category
        fields = ('id', 'parent', 'name', 'need_insurance', 'description', 'is_child_node', 'is_leaf_node', 'is_root_node')
        immutable_fields = ('parent',)

class ProductSerializer(ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'phone',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies')
        view_name = 'product-detail'
        read_only_fields = ('is_archived', 'created_at')
        immutable_fields = ('owner',)

class CarProductSerializer(ModelSerializer):
    class Meta(ProductSerializer.Meta):
        model = models.CarProduct
        fields = ProductSerializer.Meta.fields + (
            # CarProduct extended fields
            'brand', 'model', 'seat_number', 'door_number', 'fuel', 'transmission', 'mileage',
            'consumption', 'km_included', 'costs_per_km', 'air_conditioning', 'power_steering',
            'cruise_control', 'gps', 'baby_seat', 'roof_box', 'bike_rack', 'snow_tires', 'snow_chains',
            'ski_rack', 'cd_player', 'audio_input', 'tax_horsepower', 'licence_plate', 'first_registration_date',
        )

class RealEstateProductSerializer(ModelSerializer):
    class Meta(ProductSerializer.Meta):
        model = models.RealEstateProduct
        fields = ProductSerializer.Meta.fields + (
            # RealEstateProduct extended fields
            'capacity', 'private_life', 'chamber_number', 'rules', 'air_conditioning', 'breakfast', 'balcony',
            'lockable_chamber', 'towel', 'lift', 'family_friendly', 'gym', 'accessible', 'heating', 'jacuzzi',
            'chimney', 'internet_access', 'kitchen', 'smoking_accepted', 'ideal_for_events', 'tv',
            'washing_machine', 'tumble_dryer', 'computer_with_internet',
        )

class PriceSerializer(ModelSerializer):
    amount = fields.DecimalField(source='local_currency_amount', max_digits=10, decimal_places=2)

    def transform_currency(self, obj, value):
        return value and {
            'id': value,
            'symbol': obj.get_currency_display(),
        }

    class Meta:
        model = models.Price
        fields = ('id', 'product', 'name', 'amount', 'currency', 'unit')
        immutable_fields = ('product', 'currency')

class PictureSerializer(ModelSerializer):
    image = EncodedImageField(('thumbnail', 'profile', 'home', 'display'))

    class Meta:
        model = models.Picture
        fields = ('id', 'product', 'image', 'created_at')
        read_only_fields = ('created_at',)
        immutable_fields = ('product',)

class CuriositySerializer(ModelSerializer):
    class Meta:
        model = models.Curiosity
        fields = ('id', 'product')
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
