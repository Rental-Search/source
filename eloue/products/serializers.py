
from rest_framework.serializers import HyperlinkedModelSerializer

from products import models

class CategorySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'parent', 'name', 'need_insurance')
        read_only_fields = ('id', 'parent')

class CategoryDescriptionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.CategoryDescription
        fields = ('id', 'category', 'title', 'description', 'header', 'footer')
        read_only_fields = ('id', 'category')

class ProductSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'summary', 'deposit_amount', 'currency', 'description', 'address', 'phone',
                  'quantity', 'is_archived', 'category', 'owner', 'created_at', 'pro_agencies',
                  'carproduct', 'realestateproduct')
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

class PriceSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Price
        fields = ('id', 'product', 'name', 'amount')
        read_only_fields = ('id', 'product')

class PictureSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Picture
        fields = ('id', 'product', 'image', 'created_at')#, 'thumbnail', 'profile', 'home', 'display')
        read_only_fields = ('id', 'product', 'created_at')#, 'thumbnail', 'profile', 'home', 'display')
        write_only_fields = ('image',)

class CuriositySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Curiosity
        fields = ('id', 'product')

class MessageThreadSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.MessageThread
        fields = ('id', 'sender', 'recipient', 'product', 'last_message', 'subject', 'sender_archived', 'recipient_archived', 'messages')
        read_only_fields = ('id', 'sender', 'recipient', 'product', 'last_message', 'messages')

class ProductRelatedMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.ProductRelatedMessage
        fields = ('id', 'thread', 'offer')
        read_only_fields = fields
