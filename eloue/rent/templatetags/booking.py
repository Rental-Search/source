# -*- coding: utf-8 -*-
import decimal
from django.template import Library

from eloue.rent.utils import combine as combine_parts

register = Library()


@register.filter
def combine(data_list):
    return combine_parts(data_list[0], data_list[1])


@register.filter
def quantize(value, arg=None):
    number = decimal.Decimal(str(value))
    options = {
	    "ceiling": decimal.ROUND_CEILING,
	    "up": decimal.ROUND_UP,
	    "floor": decimal.ROUND_FLOOR,
	    "down": decimal.ROUND_DOWN,
	    "half-down": decimal.ROUND_HALF_DOWN,
	    "half-up": decimal.ROUND_HALF_UP
    }
    precision, rounding = None, None
    if arg:
        args = arg.split(",")
        precision, rounding = args[0], str(args[1])
    if not precision:
        precision = ".00"
    if (not rounding) or (rounding not in options):
        rounding = "floor"
    return number.quantize(decimal.Decimal(precision), rounding=options[rounding])
