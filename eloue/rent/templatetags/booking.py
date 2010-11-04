# -*- coding: utf-8 -*-
from django.template import Library

from eloue.rent.utils import combine as combine_parts

register = Library()


@register.filter
def combine(data_list):
    return combine_parts(data_list[0], data_list[1])
