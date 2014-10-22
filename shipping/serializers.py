# coding=utf-8
from django.utils.translation import gettext as _
from django.contrib.gis.geos import Point

from rest_framework.serializers import CharField, BooleanField, DecimalField, IntegerField

from eloue.api import serializers

from . import models


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
    class Meta:
        model = models.Shipping
        fields = ('id', 'booking', 'departure_point', 'arrival_point', 'price', 'token')


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
