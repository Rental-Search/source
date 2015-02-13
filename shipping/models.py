# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.contrib.gis.db import models
from django.db.models.deletion import PROTECT
from django.db.models import signals
from django.dispatch import receiver

from .choises import SHIPPING_POINT_TYPE
from .helpers import fill_order_details


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
    order_number2 = models.CharField(max_length=128, default='')
    shuttle_code2 = models.CharField(max_length=128, default='')
    shuttle_document_url2 = models.CharField(max_length=1024, default='')

@receiver(
    [signals.pre_save],
    sender=Shipping,
    dispatch_uid='shipping_fill_order_details_pre_save'
)
def on_fill_order_details_pre_save(sender, instance, **kwargs):
    fill_order_details(instance, **kwargs)
