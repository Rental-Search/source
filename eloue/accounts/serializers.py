# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from rest_framework.serializers import (
    PrimaryKeyRelatedField, CharField, EmailField,
    ValidationError
)
from rest_framework_gis.serializers import MapGeometryField

from accounts import models
from eloue.api.serializers import NullBooleanField, EncodedImageField, ModelSerializer

class GeoModelSerializer(ModelSerializer):
    field_mapping = MapGeometryField(ModelSerializer.field_mapping)

class UserSerializer(ModelSerializer):
    username = CharField(required=False, max_length=30)
    password = CharField(required=False, write_only=True, max_length=128)
    email = EmailField(required=False)
    is_professional = NullBooleanField(required=False)
    avatar = EncodedImageField(('thumbnail', 'profil', 'display', 'product_page'), required=False)
    languages = PrimaryKeyRelatedField(many=True, required=False) # TODO: remove if we got to expose language resource

    def restore_object(self, attrs, instance=None):
        # we should allow password setting on initial user registration only
        password = attrs.pop('password', None)
        user = super(UserSerializer, self).restore_object(attrs, instance=instance)
        if not instance and password:
            user.set_password(password)
        return user

    class Meta:
        model = models.Patron
        fields = ('id', 'email', 'password', 'username', 'company_name', 'is_professional', 'slug', 'avatar',
                  'default_address', 'default_number', 'about', 'work', 'school', 'hobby', 'languages',
                  'drivers_license_date', 'drivers_license_number', 'date_of_birth', 'place_of_birth', 'rib', 'url')
        read_only_fields = ('slug', 'default_address', 'default_number', 'rib', 'url', 'date_joined')
        immutable_fields = ('email', 'password', 'username')

class PasswordChangeSerializer(ModelSerializer):
    current_password = CharField(write_only=True, max_length=128)
    confirm_password = CharField(write_only=True, max_length=128)

    def restore_object(self, attrs, instance=None):
        if instance:
            instance.set_password(attrs['password'])
        return instance

    def validate_current_password(self, attrs, source):
        if not self.object.check_password(attrs[source]):
            raise ValidationError(_("Your current password was entered incorrectly. Please enter it again."))
        return attrs

    def validate_confirm_password(self, attrs, source):
        if attrs[source] != attrs['password']:
            raise ValidationError(_("The two password fields didn't match."))
        return attrs

    class Meta:
        model = models.Patron
        fields = ('password', 'current_password', 'confirm_password')
        write_only_fields = ('password',)

class AddressSerializer(GeoModelSerializer):
    street = CharField(source='address1')

    def transform_street(self, obj, value):
        return u' '.join([value, obj.address2]) if obj and obj.address2 else value

    class Meta:
        model = models.Address
        fields = ('id', 'patron', 'street', 'zipcode', 'position', 'city', 'country')
        read_only_fields = ('position',)
        immutable_fields = ('patron',)
        geo_field = 'position'

class PhoneNumberSerializer(ModelSerializer):
    class Meta:
        model = models.PhoneNumber
        fields = ('id', 'patron', 'number')
        immutable_fields = ('patron',)

class CreditCardSerializer(ModelSerializer):
    cvv = CharField(max_length=4, min_length=3, write_only=True,
        label=_(u'Cryptogramme de sécurité'),
        help_text=_(u'Les 3 derniers chiffres au dos de la carte.'),
    )

    class Meta:
        model = models.CreditCard
        fields = ('id', 'masked_number', 'expires', 'holder_name', 'card_number', 'cvv', 'holder')
        read_only_fields = ('masked_number',)
        write_only_fields = ('card_number',)
        immutable_fields = ('expires', 'holder_name', 'holder')

class ProAgencySerializer(GeoModelSerializer):
    address = CharField(source='address1')

    def transform_address(self, obj, value):
        return u' '.join([value, obj.address2]) if obj and obj.address2 else value

    class Meta:
        model = models.ProAgency
        fields = ('id', 'patron', 'name', 'phone_number', 'address', 'zipcode', 'city', 'country', 'position')
        read_only_fields = ('position',)
        immutable_fields = ('patron',)
        geo_field = 'position'

class ProPackageSerializer(ModelSerializer):
    class Meta:
        model = models.ProPackage
        fields = ('id', 'name', 'maximum_items', 'price', 'valid_from', 'valid_until')

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = ('id', 'patron', 'propackage', 'subscription_started', 'subscription_ended', 'payment_type')
        immutable_fields = ('patron', 'propackage')

class BillingSerializer(ModelSerializer):
    class Meta:
        model = models.Billing
        fields = ('id', 'patron', 'created_at')
        read_only_fields = ('created_at',)
        immutable_fields = ('patron',)

class BillingSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = models.BillingSubscription
        fields = ('subscription', 'billing', 'price')
        immutable_fields = ('subscription', 'billing')
