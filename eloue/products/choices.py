# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

from eloue.utils import Enum


UNIT = Enum([
    (0, 'HOUR', _(u'heure'), _(u'1 heure')),
    (1, 'DAY', _(u'jour'), _(u'1 jour')),
    (2, 'WEEK_END', _(u'week-end'), _(u'1 week-end')),
    (3, 'WEEK', _(u'semaine'), _(u'1 semaine')),
    (4, 'TWO_WEEKS', _(u'deux semaines'), _(u'2 semaines')),
    (5, 'MONTH', _(u'mois'), _(u'1 mois')),
])

UNITS = {
    0: lambda amount: amount,
    1: lambda amount: amount,
    2: lambda amount: amount,
    3: lambda amount: amount / 7,
    4: lambda amount: amount / 14,
    5: lambda amount: amount / 30,
}

CURRENCY = Enum([
    ('EUR', 'EUR', _(u'€')),
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
    ('geo_distance', 'NEAR', _(u"Les plus proches")),
    ('-created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
])
