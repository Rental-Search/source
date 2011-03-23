# -*- coding: utf-8 -*-
from urlparse import urljoin
from urllib import urlencode

from django.conf import settings
from django.utils.datastructures import SortedDict, MultiValueDict
from django.utils.encoding import smart_str
from django.template import Library, Node, Variable, TemplateSyntaxError
from django.utils.translation import ugettext as _


DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)

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
    return '%s%s/' % (_('location/'), '/'.join(output))


class FacetUrlNode(Node):
    def __init__(self, breadcrumbs, additions, removals):
        self.breadcrumbs = Variable(breadcrumbs)
        self.additions = [(Variable(k), Variable(v)) for k, v in additions]
        self.removals = [Variable(a) for a in removals]
    
    @staticmethod
    def urlencode(params, encoding=settings.DEFAULT_CHARSET):
        output = []
        for k, list_ in params.lists():
            k = smart_str(k, encoding)
            output.extend([urlencode({k: smart_str(v, encoding)}) for v in list_ if v])
        return '&'.join(output)
    
    def render(self, context):
        breadcrumbs = self.breadcrumbs.resolve(context).copy()
        urlbits = dict((facet['label'], facet['value']) for facet in breadcrumbs.values() if facet['facet'])
        params = MultiValueDict((facet['label'], [facet['value']]) for facet in breadcrumbs.values() if (not facet['facet']) and not (facet['label'] == 'r' and facet['value'] == DEFAULT_RADIUS))
        additions = dict([(key.resolve(context), value.resolve(context)) for key, value in self.additions])
        removals = [key.resolve(context) for key in self.removals]
        
        for key, value in additions.iteritems():
            if key in params:
                params[key] = value
            else:
                urlbits[key] = value
                
        for key in removals:
            if key in params:
                del params[key]
            if key in urlbits:
                del urlbits[key]
        
        path = urljoin('/%s' % _("location/"), ''.join(['%s/%s/' % (key, value) for key, value in urlbits.iteritems()]))
        if any([value for key, value in params.iteritems()]):
            return '%s?%s' % (path, self.urlencode(params))
        else:
            return path
    

@register.tag('facet_url')
def do_facet_url(parser, token):
    """
    {% facet_url breadcrumbs %}
    {% facet_url breadcrumbs key value %}
    {% facet_url breadcrumbs key "value again" %}
    {% facet_url breadcrumbs "key" "value again" %}
    {% facet_url breadcrumbs -key_to_remove %}
    {% facet_url breadcrumbs -"key_to_remove" %}
    
    Returns an url based on args like this one : '/filter1/foo/filter2/bar/'.
    """
    bits = token.split_contents()
    additions, removals = [], []
    breadcrumbs = bits[1]
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
    return FacetUrlNode(breadcrumbs, additions, removals)


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
        urlbits = self.sort(urlbits)
        path = urljoin('/%s' % _("location/"), ''.join(['%s/%s/' % (key, value) for key, value in urlbits.iteritems()]))
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


@register.filter
def facets(breadcrumbs):
    return [value for value in breadcrumbs.values() if value['facet']]
