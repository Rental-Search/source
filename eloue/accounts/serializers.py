
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, PrimaryKeyRelatedField, CharField
from rest_framework_gis.serializers import MapGeometryField

from accounts import models

class HyperlinkedGeoModelSerializer(HyperlinkedModelSerializer):
    field_mapping = MapGeometryField(HyperlinkedModelSerializer.field_mapping)

class UserSerializer(HyperlinkedModelSerializer):
    languages = PrimaryKeyRelatedField(many=True) # TODO: remove if we got to expose language resource

    class Meta:
        model = models.Patron
        fields = ('id', 'email', 'company_name', 'is_professional', 'slug', 'avatar', 'default_address',
                  'default_number', 'about', 'work', 'school', 'hobby', 'languages', 'drivers_license_date',
                  'drivers_license_number', 'date_of_birth', 'place_of_birth', 'rib', 'url')
        read_only_fields = ('id', 'slug', 'avatar', 'default_address', 'default_number', 'rib', 'url')

class AddressSerializer(HyperlinkedGeoModelSerializer):
    street = CharField(source='address1')

    def transform_street(self, obj, value):
        return u' '.join([value, obj.address2]) if obj and obj.address2 else value

    class Meta:
        model = models.Address
        fields = ('id', 'patron', 'street', 'zipcode', 'position', 'city', 'country')
        read_only_fields = ('id', 'patron', 'position')
        geo_field = 'position'

class PhoneNumberSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.PhoneNumber
        fields = ('id', 'patron', 'number')
        read_only_fields = ('id', 'patron')

class ProAgencySerializer(HyperlinkedGeoModelSerializer):
    address = CharField(source='address1')

    def transform_address(self, obj, value):
        return u' '.join([value, obj.address2]) if obj and obj.address2 else value

    class Meta:
        model = models.ProAgency
        fields = ('id', 'patron', 'name', 'phone_number', 'address', 'zipcode', 'city', 'country', 'position')
        read_only_fields = ('id', 'patron', 'position')
        geo_field = 'position'

class ProPackageSerializer(ModelSerializer):
    class Meta:
        model = models.ProPackage
        fields = ('id', 'name', 'maximum_items', 'price', 'valid_from', 'valid_until')
        read_only_fields = ('id', )

class SubscriptionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Subscription
        fields = ('id', 'patron', 'propackage', 'subscription_started', 'subscription_ended', 'payment_type')
        read_only_fields = ('id', 'patron', 'propackage')

class BillingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Billing
        fields = ('id', 'patron', 'created_at')
        read_only_fields = ('id', 'patron', 'created_at')

class BillingSubscriptionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.BillingSubscription
        fields = ('id', 'subscription', 'billing', 'price')
        read_only_fields = ('id', 'subscription', 'billing')
