# -*- coding: utf-8 -*-
import datetime
import time

from django.utils import formats

from eloue.rent.forms import DATE_FORMAT


def combine(date_part, time_part):
    """
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
