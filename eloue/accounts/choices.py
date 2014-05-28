# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from eloue.utils import Enum


CIVILITY_CHOICES = Enum([
    (0, 'MME', _('Madame')),
    (1, 'MLLE', _('Mademoiselle')),
    (2, 'M', _('Monsieur'))
])

COUNTRY_CHOICES = Enum([
    ('FR', 'FR', _(u'France')),
    ('BE', 'BE', _(u'Belgique')),
    ('LU', 'LU', _(u'Luxembourg')),
    ('RE', 'RE', _(u'Réunion')),
    ('DE', 'DE', _(u'Allemagne')),
    ('AD', 'AD', _(u'Andore')),
    ('AT', 'AT', _(u'Autriche')),
    ('CA', 'CA', _(u'Canada')),
    ('CY', 'CY', _(u'Chypre')),
    ('DK', 'DK', _(u'Danemark')),
    ('ES', 'ES', _(u'Espagne')),
    ('US', 'US', _(u'États-Unis')),
    ('FI', 'FI', _(u'Finlande')),
    ('GR', 'GR', _(u'Grèce')),
    ('GP', 'GP', _(u'Guadeloupe')),
    ('GG', 'GG', _(u'Guernesey')),
    ('GF', 'GF', _(u'Guyane Française')),
    ('HU', 'HU', _(u'Hongrie')),
    ('IE', 'IE', _(u'Irlande')),
    ('IS', 'IS', _(u'Islande')),
    ('IT', 'IT', _(u'Italie')),
    ('JP', 'JP', _(u'Japon')),
    ('JE', 'JE', _(u'Jersey')),
    ('LV', 'LV', _(u'Lettonie')),
    ('LI', 'LI', _(u'Liechtenstein')),
    ('LT', 'LT', _(u'Lituanie')),
    ('MT', 'MT', _(u'Malte')),
    ('MQ', 'MQ', _(u'Martinique')),
    ('MU', 'MU', _(u'Maurice')),
    ('YT', 'YT', _(u'Mayotte')),
    ('MC', 'MC', _(u'Monaco')),
    ('MA', 'MA', _(u'Maroc')),
    ('NO', 'NO', _(u'Norvège')),
    ('NC', 'NC', _(u'Nouvelle-Calédonie')),
    ('NL', 'NL', _(u'Pays-Bas')),
    ('PL', 'PL', _(u'Pologne')),
    ('PF', 'PF', _(u'Polynésie Française')),
    ('PT', 'PT', _(u'Portugal')),
    ('RO', 'RO', _(u'Roumanie')),
    ('GB', 'GB', _(u'Royaume-Uni')),
    ('RU', 'RU', _(u'Russie, Fédération de')),
    ('PM', 'PM', _(u'Saint-Pierre-et-Miquelon')),
    ('VA', 'VA', _(u'Saint-Siège (État de la cité du Vatican)')),
    ('SE', 'SE', _(u'Suède')),
    ('CH', 'CH', _(u'Suisse')),
    ('CZ', 'CZ', _(u'Tchèque, République')),
    ('TF', 'TF', _(u'Terres Australes Françaises')),
    ('TN', 'TN', _(u'Tunisie')),
    ('TR', 'TR', _(u'Turquie'))
])

PHONE_TYPES = Enum([
    (0, 'HOME', _('Domicile')),
    (1, 'WORK', _('Travail')),
    (2, 'MOBILE', _('Mobile')),
    (3, 'FAX', _('Fax')),
    (4, 'OTHER', _('Autre'))
])

SUBSCRIPTION_PAYMENT_TYPE_CHOICES = Enum([
    (0, 'CREDIT_CARD', _(u'Carte de crédit')),
    (1, 'CHECK', _(u'Chèque')),
])

GEOLOCATION_SOURCE = Enum([
    (1, 'MANUAL', _('Location set manually')),
    (2, 'BROWSER', _('Location set by browser geocoding')),
    (3, 'ADDRESS', _('Location set by user address')),
    (4, 'DEFAULT', _('Default location'))
])

STATE_CHOICES = (
    (0, _(u"Je n'ai pas encore de compte")),
    (1, _(u"J'ai déjà un compte et mon mot de passe est :")),
)

PAYPAL_ACCOUNT_CHOICES = (
    (0, _(u"Je n'ai pas encore de compte PayPal")),
    (1, _(u"J'ai déjà un compte PayPal et mon email est :")),
)
