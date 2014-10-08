# -*- coding: utf-8 -*-
import uuid

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from rest_framework.serializers import (
    PrimaryKeyRelatedField, CharField, EmailField, BooleanField, FloatField
)
from rest_framework_gis.serializers import MapGeometryField

from accounts.forms import CreditCardForm
from accounts import models
from eloue.api import serializers
from eloue.api.serializers import NestedModelSerializerMixin


class GeoModelSerializer(serializers.ModelSerializer):
    field_mapping = MapGeometryField(serializers.ModelSerializer.field_mapping)

class AddressSerializer(GeoModelSerializer):
    street = CharField(source='address1')

    def transform_street(self, obj, value):
        return u' '.join([value, obj.address2]) if obj and obj.address2 else value

    class Meta:
        model = models.Address
        fields = ('id', 'patron', 'street', 'zipcode', 'position', 'city', 'country')
        public_fields = ('zipcode', 'position', 'city', 'country')
        read_only_fields = ('position',)
        immutable_fields = ('patron',)
        geo_field = 'position'

class NestedAddressSerializer(serializers.NestedModelSerializerMixin, AddressSerializer):
    class Meta(AddressSerializer.Meta):
        public_fields = ('city', 'zipcode')


class PublicNestedAddressSerializer(serializers.NestedModelSerializerMixin, AddressSerializer):
    class Meta(AddressSerializer.Meta):
        public_fields = ('city', 'zipcode')
        fields = public_fields

class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhoneNumber
        fields = ('id', 'patron', 'number')
        immutable_fields = ('patron',)

class NestedPhoneNumberSerializer(serializers.NestedModelSerializerMixin, PhoneNumberSerializer):
    pass

class UserSerializer(serializers.ModelSerializer):
    username = CharField(required=False, max_length=30)
    password = CharField(required=False, write_only=True, max_length=128)
    email = EmailField(required=False)
    is_professional = serializers.NullBooleanField(required=False)
    avatar = serializers.EncodedImageField(('thumbnail', 'profil', 'display', 'product_page'), required=False)
    default_address = NestedAddressSerializer(required=False)
    default_number = NestedPhoneNumberSerializer(required=False)
    languages = PrimaryKeyRelatedField(many=True, required=False) # TODO: remove if we got to expose language resource
    average_note = FloatField(read_only=True)

    def restore_object(self, attrs, instance=None):
        # we should allow password setting on initial user registration only
        password = attrs.pop('password', None)
        user = super(UserSerializer, self).restore_object(attrs, instance=instance)
        if not instance and password:
            user.set_password(password)
        return user

    class Meta:
        model = models.Patron
        fields = (
            'id', 'email', 'company_name', 'username', 'first_name', 'last_name', 
            'is_professional', 'slug', 'avatar', 'default_address', 'default_number',
            'about', 'work', 'school', 'hobby', 'languages', 'drivers_license_date',
            'drivers_license_number', 'date_of_birth', 'place_of_birth', 'url',
            'date_joined', 'is_active', 'rib', 'password', 'average_note'
        )
        public_fields = (
            'id', 'company_name', 'username', 'is_professional', 'slug',
            'avatar', 'default_address', 'about', 'school', 'work', 'hobby',
            'languages', 'url', 'date_joined',
        )
        read_only_fields = ('slug', 'url', 'date_joined', 'rib')
        immutable_fields = ('email', 'password', 'username')


class NestedPublicUserSerializer(NestedModelSerializerMixin, UserSerializer):
    default_address = PublicNestedAddressSerializer()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.public_fields


class PasswordChangeSerializer(serializers.ModelSerializer):
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

class BookingPayCreditCardSerializer(serializers.ModelSerializer):
    cvv = CharField(max_length=4, min_length=3, write_only=True,
        label=_(u'Cryptogramme de sécurité'),
        help_text=_(u'Les 3 derniers chiffres au dos de la carte.'),
    )

    class Meta:
        model = models.Patron
        fields = ('creditcard', 'cvv')

class CreditCardSerializer(serializers.ModelSerializer):
    cvv = CharField(max_length=4, min_length=3, write_only=True,
        label=_(u'Cryptogramme de sécurité'),
        help_text=_(u'Les 3 derniers chiffres au dos de la carte.'),
    )
    keep = BooleanField(default=False, write_only=True)

    def validate_expires(self, attrs, source):
        try:
            expires = attrs.pop(source)
            attrs.update(dict(zip(('expires_0', 'expires_1'), (expires[:2], expires[2:4]))))
        except (KeyError, IndexError):
            raise ValidationError("Attribute missed or invalid: 'expires'")
        return attrs

    def validate(self, attrs):
        keep = attrs['keep']
        if not keep:
            attrs.pop('holder', None)
        self.form = form = CreditCardForm(attrs)
        if not form.is_valid():
            raise ValidationError('Form errors: %s' % dict(form.errors))
        new_attrs = form.clean()
        new_attrs['keep'] = keep
        return new_attrs

    def save_object(self, obj, **kwargs):
        if not obj.pk:
            obj.subscriber_reference = uuid.uuid4().hex
        elif not obj.keep and obj.holder:
            obj.holder = None
        self.form.instance = obj
        self.form.save(commit=True)

    class Meta:
        model = models.CreditCard
        fields = ('id', 'masked_number', 'expires', 'holder_name', 'card_number', 'cvv', 'holder', 'keep')
        read_only_fields = ('masked_number',)
        write_only_fields = ('card_number',)
        immutable_fields = ('expires', 'holder_name', 'holder', 'card_number', 'cvv')

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

class ProPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProPackage
        fields = ('id', 'name', 'maximum_items', 'price', 'valid_from', 'valid_until')

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = ('id', 'patron', 'propackage', 'subscription_started', 'subscription_ended', 'payment_type')
        immutable_fields = ('patron', 'propackage')

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Billing
        fields = ('id', 'patron', 'created_at')
        read_only_fields = ('created_at',)
        immutable_fields = ('patron',)

class BillingSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BillingSubscription
        fields = ('subscription', 'billing', 'price')
        immutable_fields = ('subscription', 'billing')
