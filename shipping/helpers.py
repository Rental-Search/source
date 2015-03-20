# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import re
from decimal import Decimal

from django.conf import settings
from django.contrib.gis.geos.point import Point
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from eloue.geocoder import GoogleGeocoder
from eloue.decorators import cached
from eloue.api.exceptions import ShippingException, ShippingErrorEnum

from accounts.choices import COUNTRY_CHOICES
from rent.contract import first_or_empty

from .navette import Navette, FileTransfer


SHIPPING_POINT_TO_DICT_MAP = {
    'SiteId': 'site_id',
    'PudoId': 'pudo_id',
    'Name': 'name',
    'ZipCode': 'zipcode',
    'CountryCode': 'country',
    'CountryName': 'country_name',
    'CityName': 'city',
    'AddressLine': 'address',
    'DistanceFromSearch': 'distance',
    'Latitude': 'lat',
    'Longitude': 'lng',
    'IsOpen': 'is_open',
}

OPENING_DATE_TO_DICT_MAP = {
    'AfternoonClosingTime': 'afternoon_closing_time',
    'AfternoonOpeningTime': 'afternoon_opening_time',
    'MorningClosingTime': 'morning_closing_time',
    'MorningOpeningTime': 'morning_opening_time',
    'DayOfWeek': 'day_of_week',
}

NAME_RE = re.compile(r'\d|-|_')


class EloueNavette(Navette):
    try:
        url = settings.NAVETTE_ENDPOINT
    except AttributeError:
        raise ImproperlyConfigured("NAVETTE_ENDPOINT not set.")

    try:
        wsdl_proxy = settings.WSDL_PROXY
    except AttributeError:
        wsdl_proxy = None

    def create_shipping(self, token, order_params):
        shipping_params = self.create_from_partner(token, order_params)
        return {
            'order_number': shipping_params.OrderNumber,
            'shuttle_code': shipping_params.NavetteCode,
            'shuttle_document_url': shipping_params.NavettePDFUrl
        }

    @cached(timeout=3600)
    def get_shipping_price(self, departure_point_id, arrival_point_id):
        price = self.get_price_from_partner(departure_point_id, arrival_point_id)
        return {
            'price': Decimal(price.Amount).quantize(Decimal('0.00')),
            'token': price.Token
        }

    def get_shipping_points(self, lat, lng, point_type):
        """Search nearest shipping points"""
        point_type_map = {
            1: 'Departure',
            2: 'Arrival',
        }
        shipping_points = self.get_pudo(
                Point((lat, lng)), point_type_map[point_type])
        #return [shipping_point_to_dict(FakeShippingPoint(identifier)) for identifier in xrange(6)]
        return [shipping_point_to_dict(shipping_point) for
                                shipping_point in shipping_points]

    def get_shipping_point(self, site_id, lat, lng, point_type):
        """Return shipping point info"""
        for point in self.get_shipping_points(lat, lng, point_type):
            if point['site_id'] == site_id:
                return point

        raise ShippingException({
            'code': ShippingErrorEnum.MISSING_PUDO[0],
            'description': ShippingErrorEnum.MISSING_PUDO[1],
            'detail': _(u"Can't find shipping point for lat: %s, lng: %s, type: %s, site_id: %s") % (
                lat, lng, point_type, site_id)
        })


class EloueFileTransfer(FileTransfer):
    try:
        url = settings.NAVETTE_FILE_TRANSFER_ENDPOINT
    except AttributeError:
        raise ImproperlyConfigured("NAVETTE_FILE_TRANSFER_ENDPOINT not set.")

    try:
        wsdl_proxy = settings.WSDL_PROXY
    except AttributeError:
        wsdl_proxy = None


class FakeOpeningDate(object):

    def __init__(self):
        self.AfternoonClosingTime = datetime.time(19, 30)
        self.AfternoonOpeningTime = datetime.time(15, 30)
        self.MorningClosingTime = datetime.time(12, 00)
        self.MorningOpeningTime = datetime.time(10, 00)
        self.DayOfWeek = 'Monday'


class FakeShippingPoint(object):

    def __init__(self, identifier):
        self.SiteId = identifier
        self.PudoId = 'identifier'
        self.Name = 'Test'
        self.Zipcode = '123456'
        self.CountryCode = 'Test'
        self.CityName = 'Test'
        self.AddressLine = 'Test'
        self.DistanceFromSearch = 500.5
        self.Latitude = 45.45
        self.Longitude = 22.22
        self.IsOpen = True
        self.OpeningDates = [
            (FakeOpeningDate(), )
        ]


def shipping_point_to_dict(shipping_point):
    """Convert shipping point object to dict"""
    #FIXME: Day of week not always present in response...
    opening_dates = []
    for opening_date in shipping_point.OpeningDates[0]:
        if hasattr(opening_date, 'DayOfWeek'):
            opening_dates.append(opening_date_to_dict(opening_date))

    result = {}
    for field_name, dict_key in SHIPPING_POINT_TO_DICT_MAP.items():
        result[dict_key] = None
        # FIXME: ...and any other field can be absent.
        if hasattr(shipping_point, field_name):
            result[dict_key] = getattr(shipping_point, field_name)
    result['opening_dates'] = opening_dates
    return result


def opening_date_to_dict(opening_date):
    """Convert opening date object to dict"""

    result = {}
    for field_name, dict_key in OPENING_DATE_TO_DICT_MAP.items():
        result[dict_key] = None
        # FIXME: Again, any field in response can be absent.
        if hasattr(opening_date, field_name):
            result[dict_key] = getattr(opening_date, field_name)
    return result


def get_position(address):
    """Identify geo position by address through Google service"""
    return GoogleGeocoder().geocode(address)[1]

def _get_order_date(date):
    """Return order date, 3 days max before the start date"""

    delta = date - datetime.datetime.now()

    if delta.days > 3:
        return date - datetime.deltatime(3)
    else:
        return datetime.datetime.now()


def _preprocess_name(name):
    return NAME_RE.sub(' ', name).strip()

def _fill_order_detail(delivery, dropoff, order_contact, delivery_site, dropoff_site, order_date):
    delivery_phone = delivery.default_number or first_or_empty(delivery.phones.all())
    dropoff_phone = dropoff.default_number or first_or_empty(dropoff.phones.all())

    order_contact_address = order_contact.default_address or \
                            first_or_empty(order_contact.addresses.all())
    order_contact_phone = order_contact.default_number or \
                            first_or_empty(order_contact.phones.all())

    return {
        'DeliveryContactFirstName': _preprocess_name(delivery.first_name),
        'DeliveryContactLastName': _preprocess_name(delivery.last_name),
        'DeliveryContactMail': delivery.email.replace('-', ''),
        'DeliveryContactMobil': delivery_phone.number if delivery_phone else '',
        'DeliveryContactPhone': delivery_phone.number if delivery_phone else '',
        'DeliverySiteAdress1': delivery_site.get('address', ''),
        'DeliverySiteAdress2': delivery_site.get('address2', ''),
        'DeliverySiteCity': delivery_site.get('city', ''),
        'DeliverySiteCountry': delivery_site.get('country_name', ''),
        'DeliverySiteCountryCode': delivery_site.get('country', ''),
        'DeliverySiteName': delivery_site.get('name', ''),
        'DeliverySiteZipCode': delivery_site.get('zipcode', ''),
        'DropOffContactFirstName': _preprocess_name(dropoff.first_name),
        'DropOffContactLastName': _preprocess_name(dropoff.last_name),
        'DropOffContactMail': dropoff.email.replace('-', ''),
        'DropOffContactMobil': dropoff_phone.number if dropoff_phone else '',
        'DropOffContactPhone': dropoff_phone.number if dropoff_phone else '',
        'DropOffSiteAdress1': dropoff_site.get('address', ''),
        'DropOffSiteAdress2': dropoff_site.get('address2', ''),
        'DropOffSiteCity': dropoff_site.get('city', ''),
        'DropOffSiteCountry': dropoff_site.get('country_name', ''),
        'DropOffSiteCountryCode': dropoff_site.get('country', ''),
        'DropOffSiteName': dropoff_site.get('name', ''),
        'DropOffSiteZipCode': dropoff_site.get('zipcode', ''),
        'OrderContactFirstName': _preprocess_name(order_contact.first_name),
        'OrderContactLastName': _preprocess_name(order_contact.last_name),
        'OrderContactMail': order_contact.email.replace('-', ''),
        'OrderOrderContactMobil': order_contact_phone.number if order_contact_phone else '',
        'OrderContactCivility': 1,
        'OrderSiteAdress1': order_contact_address.address1 if order_contact_address else '',
        'OrderSiteAdress2': order_contact_address.address2 if order_contact_address else '',
        'OrderSiteCity': order_contact_address.city if order_contact_address else '',
        'OrderSiteCountry': getattr(COUNTRY_CHOICES,
                     order_contact_address.country) if order_contact_address else '',
        'OrderSiteZipCode': order_contact_address.zipcode if order_contact_address else '',
        'OrderDate': order_date,
        'DeliverySiteId': delivery_site.get('site_id', ''),
        'DropOffSiteId': dropoff_site.get('site_id', ''),
    }

def fill_order_details(instance, **kwargs):
    booking = instance.booking
    product = booking.product
    owner = booking.owner
    borrower = booking.borrower
    instance.departure_point = departure_point = product.departure_point
    instance.arrival_point = arrival_point = booking.arrival_point

    navette = EloueNavette()
    product_point = product.departure_point
    product_point = navette.get_shipping_point(
                    product_point.site_id, product_point.position.x,
                    product_point.position.y, product_point.type)

    patron_point = booking.arrival_point
    patron_point = navette.get_shipping_point(
                    patron_point.site_id, patron_point.position.x,
                    patron_point.position.y, patron_point.type)

    # request Navette for the delivery from Owner to Borrower
    shipping_price = navette.get_shipping_price(departure_point.site_id, arrival_point.site_id)
    token = shipping_price['token']
    price = shipping_price['price']

    order_details = _fill_order_detail(
        owner, borrower,
        borrower,
        product_point, patron_point,
        _get_order_date(booking.started_at) 
    )
    shipping_params = navette.create_shipping(token, order_details)

    instance.order_number = shipping_params['order_number']
    instance.shuttle_code = shipping_params['shuttle_code']
    instance.shuttle_document_url = shipping_params['shuttle_document_url']

    # request Navette for the delivery from Borrower to Owner
    shipping_price = navette.get_shipping_price(arrival_point.site_id, departure_point.site_id)
    token = shipping_price['token']
    price += shipping_price['price']

    order_details = _fill_order_detail(
        borrower, owner,
        borrower,
        patron_point, product_point,
        booking.ended_at
    )
    shipping_params = navette.create_shipping(token, order_details)

    instance.order_number2 = shipping_params['order_number']
    instance.shuttle_code2 = shipping_params['shuttle_code']
    instance.shuttle_document_url2 = shipping_params['shuttle_document_url']

    # store combined price of shipping for both directions if not set already
    if not instance.price:
        instance.price = price
