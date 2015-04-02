# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.utils.translation import gettext as _
from django.contrib.gis.geos import Point

from rest_framework.fields import (
    CharField, BooleanField, DecimalField, IntegerField, TimeField
)

from eloue.api import serializers

from . import helpers, models


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

    def restore_object(self, attrs, instance=None):
        lat = attrs.pop('lat')
        lng = attrs.pop('lng')
        obj = super(ShippingPointSerializer, self).restore_object(attrs, instance=instance)
        obj.position = Point((lat, lng))
        return obj

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
