# -*- coding: utf-8 -*-
import datetime
import time

from django.utils import formats


def combine(date_part, time_part):
    if not (date_part or time_part):
        return None
    
    def to_python(value):
        for format in formats.get_format('DATE_INPUT_FORMATS'):
            try:
                return datetime.date(*time.strptime(value, format)[:3])
            except ValueError:
                continue
    date_part = to_python(date_part)
    time_part = datetime.time(*[int(part) for part in time_part.split(':')])
    return datetime.datetime.combine(date_part, time_part)
