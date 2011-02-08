# -*- coding: utf-8 -*-
import datetime
import time

from django.utils import formats
from django.utils.translation import ugettext as _

from eloue.rent.forms import DATE_FORMAT


def combine(date_part, time_part):
    """
    Combine date and time to a datetime object.
    
    >>> combine("09/10/2010", "08:00:00")
    datetime.datetime(2010, 10, 9, 8, 0)
    >>> combine("12/03/2010", "09:15:00")
    datetime.datetime(2010, 3, 12, 9, 15)
    """
    if not (date_part or time_part):
        return None
    
    def to_python(value):
        for format in combine.date_format or formats.get_format('DATE_INPUT_FORMATS'):
            try:
                return datetime.date(*time.strptime(value, format)[:3])
            except ValueError:
                continue
    date_part = to_python(date_part)
    time_part = datetime.time(*[int(part) for part in time_part.split(':')])
    return datetime.datetime.combine(date_part, time_part)
combine.date_format = DATE_FORMAT


def spellout(number, unit="", decimal=""):
    """
    Spell out numbers the dirty way.
    
    >>> spellout(123.45, 'euro', 'cent')
    'cent vingt trois euros et quarante cinq cents'
    >>> spellout(12.30, 'heure', 'minute')
    'douze heures et trente minutes'
    >>> spellout(12.03, 'heure', 'minute')
    'douze heures et trois minutes'
    >>> spellout(12.30, 'heure')
    'douze heures trente'
    >>> spellout(1.8, 'mètre')
    'un m\\xc3\\xa8tre quatre-vingt'
    >>> spellout(2.5, 'litre')
    'deux litres cinquante'
    >>> spellout(3.5)
    'trois cinquante'
    >>> spellout(300)
    'trois cents'
    >>> spellout(301)
    'trois cent un'
    >>> spellout(1000)
    'mille'
    >>> spellout(1001)
    'mille un'
    >>> spellout(1400)
    'mille quatre cents'
    >>> spellout(1401)
    'mille quatre cent un'
    >>> spellout(0)
    'z\\xc3\\xa9ro'
    >>> spellout(-650.92)
    'moins six cent cinquante'
    """
    def spell(number):
        output = ""
        if number < 20:
            output = spellout.numbers[number]
        elif number >= 20:
            if (number >= 70 and number <= 79) or (number >= 90):
                base = int(number / 10) - 1
            else:
                base = int(number / 10)
            output = spellout.tens[base]
            number = number - base * 10
            if (number == 1 or number == 11) and base < 8:
                output += " et"
            if number > 0:
                output += " %s" % decompose(number)
            else:
                output += decompose(number)
        return output

    def decompose(number):
        output = ''
        hundreds = False
        if number >= 1000000000:
            base = int(number / 1000000000)
            output += "%s %s" % (spell(base), _("milliard"))
            if base > 1:
                output += "s"
            number = number - base * 1000000000
        if number >= 1000000:
            base = int(number / 1000000)
            output += "%s %s" % (spell(base), _("million"))
            if base > 1:
                output += "s"
            number = number - base * 1000000
        if number >= 1000:
            if number >= 100000:
                base = int(number / 100000)
                if base > 1:
                    output += " %s" % spell(base)
                output += " %s" % _("cent")
                hundreds = True
                number = number - base * 100000
                if int(number / 1000) == 0 and base > 1:
                    output += "s"
            if number >= 1000:
                base = int(number / 1000)
                if (base == 1 and hundreds) or base > 1:
                    output += " %s" % spell(base)
                number = number - base * 1000
            output += " %s" % _("mille")
        if number >= 100:
            base = int(number / 100)
            if base > 1:
                output += " %s" % spell(base)
            output += " %s" % _("cent")
            number = number - base * 100
            if number == 0 and base > 1:
                output += "s"
        if number > 0:
            output += " %s" % spell(number)
        return output
    number = round(number, 2)
    integer = int(number)
    fractional = int(round((number - integer) * 100, 0))
    if integer == 0:
        output = _("zéro")
    else:
        output = decompose(abs(integer))
    if integer > 1 or integer < -1:
        if unit != '':
            output += " %ss" % unit
    else:
        output += " %s" % unit
    if fractional > 0:
        if decimal != '':
            output += " %s" % _("et")
        output += decompose(fractional)
        if fractional > 1 or fractional < -1:
            if decimal != '':
                output += " %ss" % decimal
        else:
            output += " %s" % decimal
    if number < 0:
        output = "%s %s" % (_("moins"), output)
    return output.replace('  ', ' ').strip()
spellout.numbers = [
    "", _("un"), _("deux"), _("trois"), _("quatre"), _("cinq"), _("six"), _("sept"), _("huit"), _("neuf"), _("dix"),
    _("onze"), _("douze"), _("treize"), _("quatorze"), _("quinze"), _("seize"), _("dix-sept"), _("dix-huit"), _("dix-neuf")
]
spellout.tens = [
    "", _("dix"), _("vingt"), _("trente"), _("quarante"), _("cinquante"), _("soixante"), _("soixante-dix"), _("quatre-vingt"), _("quatre-vingt-dix")
]
