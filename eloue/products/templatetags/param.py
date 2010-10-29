# -*- coding: utf-8 -*-
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError, resolve_variable

register = Library()


@register.filter
def has_param(request, param):
    return param in request.GET


@register.filter
def hash(h, key):
    if h and key in h:
        return [(key, value) for (key, value) in h[key] if value]


class AddParam(Node):
    def __init__(self, params):
        self.pairs = {}
        for pair in params.split(','):
            pair = pair.split('=')
            if len(pair) == 2:
                self.pairs[Variable(pair[0])] = Variable(pair[1])
            else:
                self.pairs[Variable(pair[0])] = None
    
    def render(self, context):
        request = resolve_variable('request', context)
        params = request.GET.copy()
        for (name, value) in self.pairs.items():
            try:
                name = name.resolve(context)
            except VariableDoesNotExist:
                pass
            if value:
                params[name] = value.resolve(context)
            elif name in params:
                del params[name]
        if params:
            return '%s?%s' % (request.path, params.urlencode())
        else:
            return request.path
    

@register.tag(name="merge")
def merge(parser, token):
    bits = token.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' tag requires an argument" % bits[0])
    return AddParam(bits[1])
