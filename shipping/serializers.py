# coding=utf-8
import datetime
from decimal import Decimal

from django.utils.translation import gettext as _
from django.contrib.gis.geos import Point
from django.core.cache import cache
from rest_framework.fields import TimeField

from rest_framework.serializers import CharField, BooleanField, DecimalField, IntegerField
from accounts.choices import COUNTRY_CHOICES

from eloue.api import serializers

from . import helpers, models
from eloue.api.exceptions import ServerException, ServerErrorEnum
from rent.contract import first_or_empty


class PudoOpeningDateSerializer(serializers.SimpleSerializer):
    afternoon_closing_time = TimeField(blank=True)
    afternoon_opening_time = TimeField(blank=True)
    day_of_week = CharField(blank=True)
    morning_closing_time = TimeField(blank=True)
    morning_opening_time = TimeField(blank=True)


class PudoSerializer(serializers.SimpleSerializer):
    name = CharField(blank=True)
    zipcode = CharField(blank=True)
    country = CharField(blank=True)
    city = CharField(blank=True)
    address = CharField(blank=True)
    distance = DecimalField(blank=True)
    is_open = BooleanField(blank=True)
    lat = DecimalField(blank=True)
    lng = DecimalField(blank=True)
    site_id = IntegerField(blank=True)
    pudo_id = CharField(blank=True)
    price = DecimalField(max_digits=10, decimal_places=2, required=False, blank=True)
    opening_dates = PudoOpeningDateSerializer(many=True, blank=True)


class ShippingPointSerializer(serializers.GeoModelSerializer):
    lat = DecimalField(required=True, write_only=True)
    lng = DecimalField(required=True, write_only=True)

    def to_native(self, obj):
        result = super(ShippingPointSerializer, self).to_native(obj)
        if obj:  # for working of REST framework GUI
            shipping_point = helpers.get_shipping_point(obj.site_id, obj.position.x, obj.position.y, obj.type)
            if shipping_point:
                extra_info = PudoSerializer(data=shipping_point)
                if extra_info.is_valid():
                    result.update(extra_info.data)
        return result

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


class NestedPatronShippingPointSerializer(serializers.NestedModelSerializerMixin, PatronShippingPointSerializer):
    pass


class NestedProductShippingPointSerializer(serializers.NestedModelSerializerMixin, ProductShippingPointSerializer):
    pass


class ShippingSerializer(serializers.ModelSerializer):

    departure_point = NestedProductShippingPointSerializer()
    arrival_point = NestedPatronShippingPointSerializer()

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
            if not token:
                price = helpers.get_shipping_price(instance.departure_point.site_id, instance.arrival_point.site_id)
                token = price.pop('token')
                if price['price'] != instance.price:
                    raise ServerException({
                        'code': ServerErrorEnum.OTHER_ERROR[0],
                        'description': ServerErrorEnum.OTHER_ERROR[1],
                        'detail': _(u'Price expired')
                    })
            shipping_params = helpers.create_shipping(token, order_details)
            # shipping_params = {
            #     'order_number': 'fake order number',
            #     'shuttle_code': 'fake shuttle code',
            #     'shuttle_document_url': 'fake shuttle document url'
            # }
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
