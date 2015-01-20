# coding=utf-8
import datetime
import re

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
            shipping_point = helpers.EloueNavette().get_shipping_point(
                        obj.site_id, obj.position.x, obj.position.y, obj.type)
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
        fields = ShippingPointSerializer.Meta.fields + ('patron', 'booking')


class ProductShippingPointSerializer(ShippingPointSerializer):

    class Meta(ShippingPointSerializer.Meta):
        model = models.ProductShippingPoint
        fields = ShippingPointSerializer.Meta.fields + ('product',)


class NestedPatronShippingPointSerializer(serializers.NestedModelSerializerMixin, PatronShippingPointSerializer):
    pass


class NestedProductShippingPointSerializer(serializers.NestedModelSerializerMixin, ProductShippingPointSerializer):
    pass


class ShippingSerializer(serializers.ModelSerializer):

    departure_point = NestedProductShippingPointSerializer(read_only=True)
    arrival_point = NestedPatronShippingPointSerializer(read_only=True)

    regexp = re.compile('\d|-|_')

    def preprocess_name(self, name):
        return self.regexp.sub(' ', name).strip()

    def _fill_order_detail(self, sender, receiver, borrower, send_point, receive_point):
        sender_address = sender.default_address or first_or_empty(sender.addresses.all())
        sender_phone = sender.default_number or first_or_empty(sender.phones.all())

        receiver_address = receiver.default_address or first_or_empty(receiver.addresses.all())
        receiver_phone = receiver.default_number or first_or_empty(receiver.phones.all())

        borrower_address = borrower.default_address or first_or_empty(borrower.addresses.all())
        borrower_phone = borrower.default_number or first_or_empty(borrower.phones.all())

        return {
            'DeliveryContactFirstName': self.preprocess_name(sender.first_name),
            'DeliveryContactLastName': self.preprocess_name(sender.last_name),
            'DeliveryContactMail': sender.email.replace('-', ''),
            'DeliveryContactMobil': sender_phone.number if sender_phone else '',
            'DeliveryContactPhone': sender_phone.number if sender_phone else '',
            'DeliverySiteAdress1': sender_address.address1 if sender_address else '',
            'DeliverySiteAdress2': sender_address.address2 if sender_address else '',
            'DeliverySiteCity': sender_address.city if sender_address else '',
            'DeliverySiteCountry': getattr(COUNTRY_CHOICES, sender_address.country) if sender_address else '',
            'DeliverySiteCountryCode': sender_address.country if sender_address else '',
            'DeliverySiteName': send_point.pudo_id,
            'DeliverySiteZipCode': sender_address.zipcode if sender_address else '',
            'DropOffContactFirstName': self.preprocess_name(receiver.first_name),
            'DropOffContactLastName': self.preprocess_name(receiver.last_name),
            'DropOffContactMail': receiver.email.replace('-', ''),
            'DropOffContactMobil': receiver_phone.number if receiver_phone else '',
            'DropOffContactPhone': receiver_phone.number if receiver_phone else '',
            'DropOffSiteAdress1': receiver_address.address1 if receiver_address else '',
            'DropOffSiteAdress2': receiver_address.address2 if receiver_address else '',
            'DropOffSiteCity': receiver_address.city if receiver_address else '',
            'DropOffSiteCountry': getattr(COUNTRY_CHOICES, receiver_address.country) if receiver_address else '',
            'DropOffSiteCountryCode': receiver_address.country if receiver_address else '',
            'DropOffSiteName': receive_point.pudo_id,
            'DropOffSiteZipCode': receiver_address.zipcode if receiver_address else '',
            'OrderContactFirstName': self.preprocess_name(borrower.first_name),
            'OrderContactLastName': self.preprocess_name(borrower.last_name),
            'OrderContactMail': borrower.email.replace('-', ''),
            'OrderOrderContactMobil': borrower_phone.number if borrower_phone else '',
            'OrderContactCivility': 1,
            'OrderSiteAdress1': borrower_address.address1 if borrower_address else '',
            'OrderSiteAdress2': borrower_address.address2 if borrower_address else '',
            'OrderSiteCity': borrower_address.city if borrower_address else '',
            'OrderSiteCountry': getattr(COUNTRY_CHOICES,
                         borrower_address.country) if borrower_address else '',
            'OrderSiteZipCode': borrower_address.zipcode if borrower_address else '',
            'OrderDate': datetime.datetime.now(),
            'DeliverySiteId': send_point.site_id,
            'DropOffSiteId': receive_point.site_id,
        }

    def from_native(self, data, files):
        instance = super(ShippingSerializer, self).from_native(data, files)
        if instance and not instance.pk:
            instance.departure_point = instance.booking.product.departure_point
            instance.arrival_point = instance.booking.arrival_point

            navette = helpers.EloueNavette()

            token = cache.get(
                helpers.build_cache_id(instance.booking.product, instance.booking.borrower, instance.arrival_point.site_id))
            if not token:
                price = navette.get_shipping_price(instance.departure_point.site_id, instance.arrival_point.site_id)
                token = price.pop('token')

            order_details = self._fill_order_detail(
                instance.booking.owner, instance.booking.borrower,
                instance.booking.borrower,
                instance.booking.product.departure_point,
                instance.booking.arrival_point)
            shipping_params = navette.create_shipping(token, order_details)

            instance.order_number = shipping_params['order_number']
            instance.shuttle_code = shipping_params['shuttle_code']
            instance.shuttle_document_url = shipping_params['shuttle_document_url']

            order_details = self._fill_order_detail(
                instance.booking.borrower, instance.booking.owner,
                instance.booking.borrower,
                instance.booking.arrival_point,
                instance.booking.product.departure_point)
            shipping_params = navette.create_shipping(token, order_details)

            instance.order_number2 = shipping_params['order_number']
            instance.shuttle_code2 = shipping_params['shuttle_code']
            instance.shuttle_document_url2 = shipping_params['shuttle_document_url']

            return instance

    class Meta:
        model = models.Shipping
        fields = ('id', 'booking', 'departure_point', 'arrival_point', 'price', 'order_number', 'shuttle_code',
                  'shuttle_document_url', 'order_number2', 'shuttle_code2', 'shuttle_document_url2')
        read_only_fields = ('order_number', 'shuttle_code', 'shuttle_document_url',
                            'order_number2', 'shuttle_code2', 'shuttle_document_url2')


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


class ShippingDocumentParamsSerializer(serializers.SimpleSerializer):
    back = BooleanField(required=True, default=False)
