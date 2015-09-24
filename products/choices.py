# -*- coding: utf-8 -*-
from decimal import Decimal as D

from django.utils.translation import ugettext as _

from products.utils import UnitEnum
from eloue.utils import Enum


def _n_days(amount, delta, rounding=True):
    return amount * (delta.days + delta.seconds / D('86400'))

def _noop(value, *args, **kwargs):
    return value

UNIT = UnitEnum([
    (0, 'HOUR', _(u'heure'),
     _(u'1 heure'),
     _noop,
     lambda amount, delta, rounding=True: amount * (delta.seconds / D('3600')),
     ),
    (1, 'DAY', _(u'jour'),
     _(u'1 jour'),
     _noop,
     lambda amount, delta, rounding=True: amount * (max(delta.days + delta.seconds / D('86400'), 1) if rounding else delta.days + delta.seconds / D('86400')),
     ),
    (2, 'WEEK_END', _(u'week-end'),
     _(u'1 week-end'),
     _noop,
     _noop,
     ),
    (3, 'WEEK', _(u'semaine'),
     _(u'1 semaine'),
     lambda amount: amount / 7,
     _n_days,
     ),
    (4, 'TWO_WEEKS', _(u'deux semaines'),
     _(u'2 semaines'),
     lambda amount: amount / 14,
     _n_days,
     ),
    (5, 'MONTH', _(u'mois'),
     _(u'1 mois'),
     lambda amount: amount / 30,
     _n_days,
     ),
    (6, 'THREE_DAYS', _(u'3jours'),
     _(u'3 jours'),
     lambda amount: amount / 3,
     _n_days,
     ),
    (7, 'FIFTEEN_DAYS', _(u'15jours'),
     _(u'15 jours'),
     lambda amount: amount / 15,
     _n_days,
     ),
])

CURRENCY = Enum([
    ('EUR', 'EUR', _(u'€')),
    ('DKK', 'DKK', _(u'kr.')),
    ('USD', 'USD', _(u'$')),
    ('GBP', 'GPB', _(u'£')),
    ('JPY', 'YEN', _(u'¥')),
    ('XPF', 'XPF', _(u'F'))
])

STATUS = Enum([
    (0, 'DRAFT', _(u'brouillon')),
    (1, 'PRIVATE', _(u'privé')),
    (2, 'PUBLIC', _(u'public')),
    (3, 'REMOVED', _(u'supprimé'))
])

PAYMENT_TYPE = Enum([
    (0, 'NOPAY', _(u'Le locataire me paye directement et mon objet n\'est pas assuré')),
    (1, 'PAYPAL', _(u'Le locataire paye en ligne et mon objet est assuré')),
    (2, 'PAYBOX', _(u'Le locataire paye en ligne par son carte bancaire et mon objet est assuré')),
])

SEAT_NUMBER = Enum([
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')),
    (7, '7', _(u'7')),
    (8, '8', _(u'8')),
    (9, '9', _(u'9')),
    (10, '10', _(u'10')),
])

DOOR_NUMBER = Enum([
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')),
])

CONSUMPTION = Enum([
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')), 
    (7, '7', _(u'7')),
    (8, '8', _(u'8')),
    (9, '9', _(u'9')),
    (10, '10', _(u'10')),
    (11, '11', _(u'11')),
    (12, '12', _(u'12')),
    (13, '13', _(u'13')),
    (14, '14', _(u'14')),
    (15, '15', _(u'15')),
    (16, '16', _(u'16')),
    (17, '17', _(u'17')),
    (18, '18', _(u'18')),
    (19, '19', _(u'19')),
])

FUEL = Enum ([
    (1, '1', _(u'Essence')),
    (2, '2', _(u'Diesel')),
    (3, '3', _(u'GPL')),
    (4, '4', _(u'Electrique')),
    (5, '5', _(u'Hybride')),
])

TRANSMISSION = Enum ([
    (1, '1', _(u'Manuel')),
    (2, '2', _(u'Automatique')),
])

MILEAGE = Enum ([
    (1, '1', _(u'- de 10000 km')),
    (2, '2', _(u'Entre 10001 et 50000 km')),
    (3, '3', _(u'Plus de 50000 km')),
])

CAPACITY = Enum ([
    (1, '1', _(u'1')),
    (2, '2', _(u'2')),
    (3, '3', _(u'3')),
    (4, '4', _(u'4')),
    (5, '5', _(u'5')),
    (6, '6', _(u'6')), 
    (7, '7', _(u'7')),
    (8, '8', _(u'8')),
    (9, '9', _(u'9')),
    (10, '10', _(u'10')),
    (11, '11', _(u'11')),
    (12, '12', _(u'12')),
    (13, '13', _(u'13')),
    (14, '14', _(u'14')),
    (15, '15', _(u'15')),
    (16, '16', _(u'16')),
    (17, '17', _(u'17')),
    (18, '18', _(u'18')),
    (19, '19', _(u'19+')),
])

TAX_HORSEPOWER = CAPACITY

PRIVATE_LIFE = Enum([
    (1, '1', _(u'Appartement/Maison')),
    (2, '2', _(u'Chambre partagé')),
    (3, '3', _(u'Chambre privée')),
])

SORT = Enum([
    ('distance', 'NEAR', _(u"Les plus proches")),
    ('-created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
])

SORT_SEARCH_RESULT = Enum([
    ('distance', 'NEAR', _(u"Les plus proches")),
    ('-created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
    ('average_rate', 'WORSE_RATE', _(u"Les ...")),  # TODO Translate
    ('-average_rate', 'BETTER_RATE', _(u"Les ...")),  # TODO Translate
])

PRODUCT_TYPE = Enum([
    (2700, 'CAR', _(u"Location Automobile")),
    (2713, 'REALESTATE', _(u"Location saisonnière")),
])
