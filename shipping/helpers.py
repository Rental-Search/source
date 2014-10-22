# coding=utf-8
from django.contrib.gis.geos.point import Point
from eloue.geocoder import GoogleGeocoder
from shipping.choises import SHIPPING_POINT_TYPE
from shipping.navette import Navette


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
        self.price = 3.9


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
    'price': 'price',
}


def build_cache_id(product, user, site_id):
    return '{}_{}_{}_shipping_token'.format(product.id, user.id, site_id)


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
