# coding=utf-8
from django.utils.translation import gettext as _
from eloue.utils import Enum


SHIPPING_POINT_TYPE = Enum([
    (1, 'Departure', _('Pudo de type départ')),
    (2, 'Arrival', _('Pudo de type arrivée')),
])
