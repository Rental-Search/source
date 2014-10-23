# coding=utf-8
import datetime
from django.contrib.gis.geos.point import Point
from eloue.geocoder import GoogleGeocoder
from shipping.choises import SHIPPING_POINT_TYPE
from shipping.navette import Navette


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
        self.Latitude = 123.456
        self.Longitude = 123.456
        self.IsOpen = True
        self.OpeningDates = [
            FakeOpeningDate()
        ]
        self.price = 3.9


SHIPPING_POINT_TO_DICT_MAP = {
    'SiteId': 'site_id',
    'PudoId': 'pudo_id',
    'Name': 'name',
    'Zipcode': 'zipcode',
    'CountryCode': 'country',
    'CityName': 'city',
    'AddressLine': 'address',
    'DistanceFromSearch': 'distance',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'IsOpen': 'is_open',
    'price': 'price',
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
    opening_dates = [opening_date_to_dict(opening_date) for opening_date in shipping_point.OpeningDates]

    result = {
        dict_key: getattr(shipping_point, field_name) for field_name, dict_key in SHIPPING_POINT_TO_DICT_MAP.items()
    }
    result['opening_dates'] = opening_dates
    return result


def opening_date_to_dict(opening_date):
    """Convert opening date object to dict"""
    return {
        dict_key: getattr(opening_date, field_name) for field_name, dict_key in OPENING_DATE_TO_DICT_MAP.items()
    }


def get_position(address):
    """Identify geo position by address through Google service"""
    return GoogleGeocoder().geocode(address)[1]


def get_shipping_points(lat, lng, point_type):
    """Search nearest shipping points"""
    point_type_map = {
        1: 'Departure',
        2: 'Arrival',
    }
    shipping_points = Navette().get_pudo(Point((lat, lng)), point_type_map[point_type])
    return [shipping_point_to_dict(FakeShippingPoint(identifier)) for identifier in xrange(6)]
    return [shipping_point_to_dict(shipping_point) for shipping_point in shipping_points]


def get_shipping_point(site_id, lat, lng, point_type):
    """Return shipping point info"""
    try:
        return filter(lambda x: x['site_id'] == site_id, get_shipping_points(lat, lng, point_type))[0]
    except IndexError:
        return None


def get_shipping_price(departure_point_id, arrival_point_id):
    price = Navette().get_price_from_partner(departure_point_id, arrival_point_id)
    return {'price': price.Amount, 'token': price.Token}


def create_shipping(token, order_params):
    shipping_params = Navette().create_from_partner(token, **order_params)
    return {
        'order_number': shipping_params.OrderNumber,
        'shuttle_code': shipping_params.NavetteCode,
        'shuttle_document_url': shipping_params.NavettePDFUrl
    }
