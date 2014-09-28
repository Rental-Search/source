# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from eloue.utils import Enum


BOOKING_STATE = Enum([
    ('authorizing', 'AUTHORIZING', _(u"En cours d'autorisation")),
    ('authorized', 'AUTHORIZED', _(u"En attente")),
    ('rejected', 'REJECTED', _(u'Rejeté')),
    ('canceled', 'CANCELED', _(u'Annulé')),
    ('pending', 'PENDING', _(u'A venir')),
    ('ongoing', 'ONGOING', _(u'En cours')),
    ('ended', 'ENDED', _(u'Terminé')),
    ('incident', 'INCIDENT', _(u'Incident')),
    ('refunded', 'REFUNDED', _(u'Remboursé')), # NOTE: not used today
    ('deposit', 'DEPOSIT', _(u'Caution versée')), # NOTE: not used today
    ('closing', 'CLOSING', _(u"En attende de clôture")), # NOTE: not used today
    ('closed', 'CLOSED', _(u'Clôturé')),
    ('outdated', 'OUTDATED', _(u"Dépassé")),
    ('unaccepted', 'UNACCEPTED', _(u"Pas accepté")), # NOTE: not used today
    ('accepted_unauthorized', 'ACCEPTED_UNAUTHORIZED', _(u"Accepté et en cours d'autorisation")), # NOTE: not used today
    ('professional', 'PROFESSIONAL', _(u"Demande pro")),
    ('professional_saw', 'PROFESSIONAL_SAW', _(u'Lu')),
])

TIME_CHOICE = (
    ('00:00:00', '00h'),
    ('01:00:00', '01h'),
    ('02:00:00', '02h'),
    ('03:00:00', '03h'),
    ('04:00:00', '04h'),
    ('05:00:00', '05h'),
    ('06:00:00', '06h'),
    ('07:00:00', '07h'),
    ('08:00:00', '08h'),
    ('09:00:00', '09h'),
    ('10:00:00', '10h'),
    ('11:00:00', '11h'),
    ('12:00:00', '12h'),
    ('13:00:00', '13h'),
    ('14:00:00', '14h'),
    ('15:00:00', '15h'),
    ('16:00:00', '16h'),
    ('17:00:00', '17h'),
    ('18:00:00', '18h'),
    ('19:00:00', '19h'),
    ('20:00:00', '20h'),
    ('21:00:00', '21h'),
    ('22:00:00', '22h'),
    ('23:00:00', '23h')
)

COMMENT_TYPE_CHOICES = Enum([
    (0, 'OWNER', _('OwnerComment')),
    (1, 'BORROWER', _('BorrowerComment')),
])
