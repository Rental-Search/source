# coding=utf-8
from django.utils.translation import gettext as _
from django.contrib.gis.geos import Point

from rest_framework.serializers import CharField, BooleanField, DecimalField, IntegerField

from eloue.api import serializers

from . import models


class ShippingPointSerializer(serializers.SimpleSerializer):
    site_id = IntegerField()
    name = CharField()
    zipcode = CharField()
    country = CharField()
    city = CharField()
    address = CharField()
    distance = DecimalField()
    latitude = DecimalField()
    longitude = DecimalField()
    is_open = BooleanField()


class AbstractShippingPointSerializer(serializers.GeoModelSerializer):
    lat = DecimalField(write_only=True, required=True)
    lng = DecimalField(write_only=True, required=True)

    def save_object(self, obj, **kwargs):
        obj.position = Point((obj.lat, obj.lng))
        super(AbstractShippingPointSerializer, self).save_object(obj, **kwargs)

    class Meta:
        fields = ('id', 'patron', 'site_id', 'position', 'type', 'lat', 'lng')
        read_only_fields = ('position',)


class PatronShippingPointSerializer(AbstractShippingPointSerializer):

    class Meta(AbstractShippingPointSerializer.Meta):
        model = models.PatronShippingPoint
        fields = AbstractShippingPointSerializer.Meta.fields + ('patron',)


class ProductShippingPointSerializer(AbstractShippingPointSerializer):

    class Meta(AbstractShippingPointSerializer.Meta):
        model = models.ProductShippingPoint
        fields = AbstractShippingPointSerializer.Meta.fields + ('product',)


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


class ShippingPointRetrieveParamsSerializer(serializers.SimpleSerializer):
    lat = DecimalField(required=True)
    lng = DecimalField(required=True)
    search_type = IntegerField(required=True)
