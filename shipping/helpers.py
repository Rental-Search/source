# coding=utf-8
import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.gis.geos.point import Point
from django.core.exceptions import ImproperlyConfigured

from eloue.geocoder import GoogleGeocoder
from shipping.navette import Navette, FileTransfer


class EloueNavette(Navette):
    try:
        url = settings.NAVETTE_ENDPOINT
    except AttributeError:
        raise ImproperlyConfigured("NAVETTE_ENDPOINT not set.")

    wsdl_proxy = settings.WSDL_PROXY


class EloueFileTransfer(FileTransfer):
    try:
        url = settings.NAVETTE_FILE_TRANSFER_ENDPOINT
    except AttributeError:
        raise ImproperlyConfigured("NAVETTE_FILE_TRANSFER_ENDPOINT not set.")

    wsdl_proxy = settings.WSDL_PROXY


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


SHIPPING_POINT_TO_DICT_MAP = {
    'SiteId': 'site_id',
    'PudoId': 'pudo_id',
    'Name': 'name',
    'ZipCode': 'zipcode',
    'CountryCode': 'country',
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


def build_cache_id(product, user, site_id):
    return '{}_{}_{}_shipping_token'.format(product.id, user.id, site_id)


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


def get_shipping_points(lat, lng, point_type):
    """Search nearest shipping points"""
    point_type_map = {
        1: 'Departure',
        2: 'Arrival',
    }
    shipping_points = EloueNavette().get_pudo(Point((lat, lng)), point_type_map[point_type])
    #return [shipping_point_to_dict(FakeShippingPoint(identifier)) for identifier in xrange(6)]
    return [shipping_point_to_dict(shipping_point) for shipping_point in shipping_points]


def get_shipping_point(site_id, lat, lng, point_type):
    """Return shipping point info"""
    try:
        return filter(lambda x: x['site_id'] == site_id, get_shipping_points(lat, lng, point_type))[0]
    except IndexError:
        return None


def get_shipping_price(departure_point_id, arrival_point_id):
    price = EloueNavette().get_price_from_partner(departure_point_id, arrival_point_id)
    return {'price': Decimal(price.Amount).quantize(Decimal('0.00')), 'token': price.Token}


def create_shipping(token, order_params):
    shipping_params = EloueNavette().create_from_partner(token, order_params)
    return {
        'order_number': shipping_params.OrderNumber,
        'shuttle_code': shipping_params.NavetteCode,
        'shuttle_document_url': shipping_params.NavettePDFUrl
    }


def get_shipping_document(filename):
    return EloueFileTransfer().download_etiquette(filename)
