# coding=utf-8
from eloue.geocoder import GoogleGeocoder


class FakeShippingPoint(object):

    def __init__(self, identifier):
        self.site_id = identifier
        self.name = 'Test'
        self.zipcode = '123456'
        self.country = 'Test'
        self.city = 'Test'
        self.address = 'Test'
        self.distance = 500.5
        self.latitude = 123.456
        self.longitude = 123.456
        self.is_open = True


SHIPPING_POINT_TO_DICT_MAP = {
    'site_id': 'site_id',
    'name': 'name',
    'zipcode': 'zipcode',
    'country': 'country',
    'city': 'city',
    'address': 'address',
    'distance': 'distance',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'is_open': 'is_open',
}


def shipping_point_to_dict(shipping_point):
    """Convert shipping point object to dict"""
    return {
        dict_key: getattr(shipping_point, field_name) for field_name, dict_key in SHIPPING_POINT_TO_DICT_MAP.items()
    }


def get_position(address):
    """Identify geo position by address through Google service"""
    return GoogleGeocoder().geocode(address)[1]


def get_shipping_points(lat, lng, point_type):
    """Search nearest shipping points"""
    return [shipping_point_to_dict(FakeShippingPoint(identifier)) for identifier in xrange(6)]


def get_shipping_point(site_id, lat, lng, point_type):
    """Return shipping point info"""
    return filter(lambda x: x['site_id'] == site_id, get_shipping_points(lat, lng, point_type))


def get_shipping_price(departure_point_id, arrival_point_id):
    return {'price': 123.45, 'token': '123456'}
