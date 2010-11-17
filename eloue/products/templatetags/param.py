# -*- coding: utf-8 -*-
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError, resolve_variable

register = Library()


@register.filter
def has_param(request, param):
    """
    >>> class DummyRequest(object):
    ...     pass
    >>> request = DummyRequest()
    >>> request.GET = {'q': 'banana'}
    >>> has_param(request, 'q')
    True
    >>> has_param(request, 'l')
    False
    """
    return param in request.GET


@register.filter
def hash(h, key):
    """
    >>> hash({'fruit': (('banana', 1),)}, 'fruit')
    [('banana', 1)]
    >>> hash({'fruit': (('banana', 1),)}, 'vegetables')
    """
    if h and key in h:
        return [(key, value) for (key, value) in h[key] if value]

