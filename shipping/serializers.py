# coding=utf-8
import datetime

from django.utils.translation import gettext as _
from django.contrib.gis.geos import Point
from django.core.cache import cache
from rest_framework.fields import TimeField

from rest_framework.serializers import CharField, BooleanField, DecimalField, IntegerField
from accounts.choices import COUNTRY_CHOICES

from eloue.api import serializers

from . import helpers, models
from rent.contract import first_or_empty


class PudoOpeningDateSerializer(serializers.SimpleSerializer):
    afternoon_closing_time = TimeField()
    afternoon_opening_time = TimeField()
    day_of_week = CharField()
    morning_closing_time = TimeField()
    morning_opening_time = TimeField()


class PudoSerializer(serializers.SimpleSerializer):
    name = CharField()
    zipcode = CharField()
    country = CharField()
    city = CharField()
    address = CharField()
    distance = DecimalField()
    is_open = BooleanField()
    latitude = DecimalField()
    longitude = DecimalField()
    opening_dates = PudoOpeningDateSerializer(many=True)


class ShippingPointSerializer(serializers.GeoModelSerializer):
    lat = DecimalField(required=True, write_only=True)
    lng = DecimalField(required=True, write_only=True)

    def save_object(self, obj, **kwargs):
        obj.position = Point((obj.lat, obj.lng))
        super(ShippingPointSerializer, self).save_object(obj, **kwargs)

    class Meta:
        model = models.ShippingPoint
        fields = ('id', 'site_id', 'pudo_id', 'position', 'type', 'lat', 'lng')
        read_only_fields = ('position',)


class PatronShippingPointSerializer(ShippingPointSerializer):

    class Meta(ShippingPointSerializer.Meta):
        model = models.PatronShippingPoint
        fields = ShippingPointSerializer.Meta.fields + ('patron',)


class ProductShippingPointSerializer(ShippingPointSerializer):

    class Meta(ShippingPointSerializer.Meta):
        model = models.ProductShippingPoint
        fields = ShippingPointSerializer.Meta.fields + ('product',)


class ShippingSerializer(serializers.ModelSerializer):

    def from_native(self, data, files):
        instance = super(ShippingSerializer, self).from_native(data, files)
        if instance and not instance.pk:
            owner = instance.booking.owner
            borrower = instance.booking.borrower

            owner_address = owner.default_address or first_or_empty(owner.addresses.all())
            owner_phone = owner.default_number or first_or_empty(owner.phones.all())
            borrower_address = borrower.default_address or first_or_empty(borrower.addresses.all())
            borrower_phone = borrower.default_number or first_or_empty(borrower.phones.all())

            order_details = {
                'DeliveryContactFirstName': owner.first_name,
                'DeliveryContactLastName': owner.last_name,
                'DeliveryContactMail': owner.email,
                'DeliveryContactMobil': owner_phone.number if owner_phone else '',
                'DeliveryContactPhone': owner_phone.number if owner_phone else '',
                'DeliverySiteAdress1': owner_address.address1 if owner_address else '',
                'DeliverySiteAdress2': owner_address.address2 if owner_address else '',
                'DeliverySiteCity': owner_address.city if owner_address else '',
                'DeliverySiteCountry': getattr(COUNTRY_CHOICES, owner_address.country) if owner_address else '',
                'DeliverySiteCountryCode': owner_address.country if owner_address else '',
                'DeliverySiteName': 'test',
                'DeliverySiteZipCode': owner_address.zipcode if owner_address else '',
                'DropOffContactFirstName': borrower.first_name,
                'DropOffContactLastName': borrower.last_name,
                'DropOffContactMail': borrower.email,
                'DropOffContactMobil': borrower_phone.number if borrower_phone else '',
                'DropOffContactPhone': borrower_phone.number if borrower_phone else '',
                'DropOffSiteAdress1': borrower_address.address1 if borrower_address else '',
                'DropOffSiteAdress2': borrower_address.address2 if borrower_address else '',
                'DropOffSiteCity': borrower_address.city if borrower_address else '',
                'DropOffSiteCountry': getattr(COUNTRY_CHOICES, borrower_address.country) if borrower_address else '',
                'DropOffSiteCountryCode': borrower_address.country if borrower_address else '',
                'DropOffSiteName': 'test',
                'DropOffSiteZipCode': borrower_address.zipcode if borrower_address else '',
                'OrderContactFirstName': 'TEST',
                'OrderContactLastName': 'Test',
                'OrderContactMail': 'test@test.com',
                'OrderOrderContactMobil': '0648484848',
                'OrderContactCivility': 1,
                'OrderSiteAdress1': 'test',
                'OrderSiteAdress2': 'test',
                'OrderSiteCity': 'test',
                'OrderSiteCountry': 'france',
                'OrderSiteZipCode': '75011',
                'OrderDate': datetime.datetime.now(),
                'OrderId': 'B400003a-abcd',
                'DeliverySiteId': instance.departure_point.site_id,
                'DropOffSiteId': instance.arrival_point.site_id,
            }
            token = cache.get(
                helpers.build_cache_id(instance.booking.product, instance.booking.borrower, instance.arrival_point.site_id))
            shipping_params = helpers.create_shipping(token, order_details)
            instance.order_number = shipping_params['order_number']
            instance.shuttle_code = shipping_params['shuttle_code']
            instance.shuttle_document_url = shipping_params['shuttle_document_url']
            return instance

    class Meta:
        model = models.Shipping
        fields = ('id', 'booking', 'departure_point', 'arrival_point', 'price', 'order_number', 'shuttle_code',
                  'shuttle_document_url')
        read_only_fields = ('order_number', 'shuttle_code', 'shuttle_document_url')


class ShippingPointListParamsSerializer(serializers.SimpleSerializer):
    lat = DecimalField(required=False, default=None)
    lng = DecimalField(required=False, default=None)
    address = CharField(required=False)
    search_type = IntegerField(required=True)

    def perform_validation(self, attrs):
        super(ShippingPointListParamsSerializer, self).perform_validation(attrs)
        position_in_params = 'lng' in attrs and 'lat' in attrs
        address_in_params = 'address' in attrs
        if not any([position_in_params, address_in_params]):
            msg = _(u'Latitude\longitude or address are required')
            self._errors['lng'] = msg
            self._errors['lat'] = msg
            self._errors['address'] = msg
        return attrs
