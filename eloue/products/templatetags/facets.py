# -*- coding: utf-8 -*-
from urlparse import urljoin

from django.utils.datastructures import SortedDict
from django.template import Library, Node, Variable, TemplateSyntaxError

register = Library()

@register.simple_tag
def facet_breadcrumb_link(breadcrumbs, facet):
    """
    {% facet_breadcrumb_link breadcrumbs facet %}
    """
    output = []
    for f in breadcrumbs.values():
        output.append(f['url'])
        if f == facet:
            break
    return '%s/%s/' % ('location', '/'.join(output))

class FacetUrlNode(Node):
    def __init__(self, urlbits, additions, removals):
        self.query = Variable('query')
        self.urlbits = Variable(urlbits)
        self.additions = [(Variable(k), Variable(v)) for k, v in additions]
        self.removals = [Variable(a) for a in removals]
    
    def render(self, context):
        urlbits = self.urlbits.resolve(context).copy()
        query = self.query.resolve(context)
        del urlbits['query']
        del urlbits['where']
        for key, value in self.additions:
            urlbits[key.resolve(context)] = value.resolve(context)
        for key in self.removals:
            try:
                del urlbits[key.resolve(context)]
            except KeyError:
                pass
        path = urljoin('/location/', ''.join([ '%s/%s/' % (key, value) for key, value in urlbits.iteritems() ]))
        if query:
            return "%s?q=%s" % (path, query)
        else:
            return path
    

@register.tag('facet_url')
def do_facet_url(parser, token):
    """
    {% facet_url urlbits %}
    {% facet_url urlbits key value %}
    {% facet_url urlbits key "value again" %}
    {% facet_url urlbits "key" "value again" %}
    {% facet_url urlbits -key_to_remove %}
    {% facet_url urlbits -"key_to_remove" %}
    
    Returns an url based on args like this one : '/filter1/foo/filter2/bar/'.
    """
    bits = token.split_contents()
    additions, removals = [], []
    urlbits = bits[1]
    stack = bits[:1:-1]
    while stack:
        bit = stack.pop()
        if bit.startswith('-'):
            removals.append(bit[1:])
        else:
            try:
                next_bit = stack.pop()
            except IndexError:
                raise TemplateSyntaxError('Invalid argument length: %r' % token)
            additions.append((bit, next_bit))
    return FacetUrlNode(urlbits, additions, removals)

class CanonicalNode(Node):
    def __init__(self, urlbits):
        self.urlbits = Variable(urlbits)
    
    def sort(self, bits):
        urlbits = SortedDict()
        keys = bits.keys()
        keys.sort()
        for key in keys:
            urlbits[key] = bits[key]
        return urlbits
    
    def render(self, context):
        urlbits = self.urlbits.resolve(context).copy()
        del urlbits['query']
        del urlbits['where']
        urlbits = self.sort(urlbits)
        path = urljoin('/location/', ''.join([ '%s/%s/' % (key, value) for key, value in urlbits.iteritems() ]))
        return path
    

@register.tag('canonical_url')
def do_canonical_url(parser, token):
    """
    {% canonical_url urlbits %}
    
    Returns a an canonical url like this one : '/par-abc/foo/par-bcd/bar/'
    """
    bits = token.split_contents()
    urlbits = bits[1]
    return CanonicalNode(urlbits)
