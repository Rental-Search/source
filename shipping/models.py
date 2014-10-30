# coding=utf-8
from django.contrib.gis.db import models
from django.db.models.deletion import PROTECT
from shipping.choises import SHIPPING_POINT_TYPE


class ShippingPoint(models.Model):
    site_id = models.BigIntegerField()
    pudo_id = models.CharField(max_length=128)
    position = models.PointField()
    type = models.SmallIntegerField(choices=SHIPPING_POINT_TYPE)


class PatronShippingPoint(ShippingPoint):
    patron = models.ForeignKey('accounts.Patron', related_name='shipping_points')
    booking = models.OneToOneField('rent.Booking', related_name='arrival_point', null=True)


class ProductShippingPoint(ShippingPoint):
    product = models.OneToOneField('products.Product', related_name='departure_point')


class Shipping(models.Model):
    booking = models.OneToOneField('rent.Booking', related_name='shipping')
    departure_point = models.ForeignKey(ProductShippingPoint, on_delete=PROTECT, related_name='+')
    arrival_point = models.ForeignKey(PatronShippingPoint, on_delete=PROTECT, related_name='+')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_number = models.CharField(max_length=128, default='')
    shuttle_code = models.CharField(max_length=128, default='')
    shuttle_document_url = models.CharField(max_length=1024, default='')
