# -*- coding: utf-8 -*-
import datetime
import time

from django.template import Library
from django.utils import formats

register = Library()


@register.filter
def combine(data_list):
    def to_python(value):
        for format in formats.get_format('DATE_INPUT_FORMATS'):
            try:
                return datetime.date(*time.strptime(value, format)[:3])
            except ValueError:
                continue
    date_part = to_python(data_list[0])
    time_part = datetime.time(*[int(part) for part in data_list[1].split(':')])
    return datetime.datetime.combine(date_part, time_part)
