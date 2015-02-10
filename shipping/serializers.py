# coding=utf-8
import datetime
import re

from django.utils.translation import gettext as _
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.core.exceptions import ValidationError
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

    def _fill_order_detail(self, delivery, dropoff, order_contact,
                                    delivery_site, dropoff_site):
        delivery_phone = delivery.default_number or first_or_empty(delivery.phones.all())
        dropoff_phone = dropoff.default_number or first_or_empty(dropoff.phones.all())

        order_contact_address = order_contact.default_address or \
                                first_or_empty(order_contact.addresses.all())
        order_contact_phone = order_contact.default_number or \
                                first_or_empty(order_contact.phones.all())

        return {
            'DeliveryContactFirstName': self.preprocess_name(delivery.first_name),
            'DeliveryContactLastName': self.preprocess_name(delivery.last_name),
            'DeliveryContactMail': delivery.email.replace('-', ''),
            'DeliveryContactMobil': delivery_phone.number if delivery_phone else '',
            'DeliveryContactPhone': delivery_phone.number if delivery_phone else '',
            'DeliverySiteAdress1': delivery_site.get('address', ''),
            'DeliverySiteAdress2': delivery_site.get('address2', ''),
            'DeliverySiteCity': delivery_site.get('city', ''),
            'DeliverySiteCountry': delivery_site.get('country_name', ''),
            'DeliverySiteCountryCode': delivery_site.get('country', ''),
            'DeliverySiteName': delivery_site.get('pudo_id', ''),
            'DeliverySiteZipCode': delivery_site.get('zipcode', ''),
            'DropOffContactFirstName': self.preprocess_name(dropoff.first_name),
            'DropOffContactLastName': self.preprocess_name(dropoff.last_name),
            'DropOffContactMail': dropoff.email.replace('-', ''),
            'DropOffContactMobil': dropoff_phone.number if dropoff_phone else '',
            'DropOffContactPhone': dropoff_phone.number if dropoff_phone else '',
            'DropOffSiteAdress1': dropoff_site.get('address', ''),
            'DropOffSiteAdress2': dropoff_site.get('address2', ''),
            'DropOffSiteCity': dropoff_site.get('city', ''),
            'DropOffSiteCountry': dropoff_site.get('country_name', ''),
            'DropOffSiteCountryCode': dropoff_site.get('country', ''),
            'DropOffSiteName': dropoff_site.get('pudo_id', ''),
            'DropOffSiteZipCode': delivery_site.get('zipcode', ''),
            'OrderContactFirstName': self.preprocess_name(order_contact.first_name),
            'OrderContactLastName': self.preprocess_name(order_contact.last_name),
            'OrderContactMail': order_contact.email.replace('-', ''),
            'OrderOrderContactMobil': order_contact_phone.number if order_contact_phone else '',
            'OrderContactCivility': 1,
            'OrderSiteAdress1': order_contact_address.address1 if order_contact_address else '',
            'OrderSiteAdress2': order_contact_address.address2 if order_contact_address else '',
            'OrderSiteCity': order_contact_address.city if order_contact_address else '',
            'OrderSiteCountry': getattr(COUNTRY_CHOICES,
                         order_contact_address.country) if order_contact_address else '',
            'OrderSiteZipCode': order_contact_address.zipcode if order_contact_address else '',
            'OrderDate': datetime.datetime.now(),
            'DeliverySiteId': delivery_site.get('site_id', ''),
            'DropOffSiteId': dropoff_site.get('site_id', ''),
        }

    def from_native(self, data, files):
        instance = super(ShippingSerializer, self).from_native(data, files)
        if instance and not instance.pk:
            instance.departure_point = instance.booking.product.departure_point
            instance.arrival_point = instance.booking.arrival_point

            navette = helpers.EloueNavette()
            product_point = instance.booking.product.departure_point
            product_point = navette.get_shipping_point(
                            product_point.site_id, product_point.position.x, 
                            product_point.position.y, product_point.type)

            patron_point = instance.booking.arrival_point
            patron_point = navette.get_shipping_point(
                            patron_point.site_id, patron_point.position.x, 
                            patron_point.position.y, patron_point.type)

            token = cache.get(
                helpers.build_cache_id(instance.booking.product, instance.booking.borrower, instance.arrival_point.site_id))
            if not token:
                price = navette.get_shipping_price(instance.departure_point.site_id, instance.arrival_point.site_id)
                token = price.pop('token')

            order_details = self._fill_order_detail(
                instance.booking.owner, instance.booking.borrower,
                instance.booking.borrower,
                product_point, patron_point)
            shipping_params = navette.create_shipping(token, order_details)

            instance.order_number = shipping_params['order_number']
            instance.shuttle_code = shipping_params['shuttle_code']
            instance.shuttle_document_url = shipping_params['shuttle_document_url']

            order_details = self._fill_order_detail(
                instance.booking.borrower, instance.booking.owner,
                instance.booking.borrower,
                patron_point, product_point)
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
