# -*- coding: utf-8 -*-
from django.template import Library

register = Library()


@register.filter
def from_lupa(request):
    if 'HTTP_REFERER' in request.META:
        return "loueunepetiteamie.com" in request.META['HTTP_REFERER']
    elif 'lupa' in request.GET:
        return True
    else:
        return False

