# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_detail, object_list

from geocoders.google import geocoder
from haystack.query import SearchQuerySet

from eloue.accounts.models import Patron
from eloue.products.forms import FacetedSearchForm, ProductSearchForm
from eloue.products.models import Product, Category

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 20)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)

@cache_page(300)
def homepage(request):
    form = FacetedSearchForm()
    return direct_to_template(request, template='index.html', extra_context={ 'form':form })

@cache_page(900)
def product_detail(request, slug, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.slug != slug:
        return redirect_to(request, product.get_absolute_url())
    return direct_to_template(request, template='products/product_detail.html', extra_context={ 'product':product })

@cache_page(900)
@vary_on_cookie
def product_list(request, urlbits, sqs = SearchQuerySet(), suggestions = None, page = None):
    query = request.GET.get('q', None)
    if query:
        sqs = sqs.auto_query(query).highlight()
        suggestions = sqs.spelling_suggestion()
    
    where, radius = request.GET.get('where', None), request.GET.get('radius', None)
    if where:
        coordinates = cache.get('where:%s' % where.lower())
        if not coordinates:
            geocode = geocoder(settings.GOOGLE_API_KEY)
            name, coordinates = geocode(where)
            cache.set('where:%s' % where.lower(), coordinates, 0)
        sqs = sqs.spatial(lat=coordinates[0], long=coordinates[1], radius=radius if radius else DEFAULT_RADIUS, unit='km')
        
    breadcrumbs = SortedDict()
    breadcrumbs['q'] = { 'name':'q', 'value':query, 'label':'q', 'facet':False }
    breadcrumbs['where'] = { 'name':'where', 'value':where, 'label':'where', 'facet':False }
    breadcrumbs['sort'] = { 'name':'sort', 'value':request.GET.get('sort', None), 'label':'sort', 'facet':False }
    breadcrumbs['radius'] = { 'name':'radius', 'value':radius, 'label':'radius', 'facet':False }
    urlbits = urlbits or ''
    urlbits = filter(None, urlbits.split('/')[::-1])
    while urlbits:
        bit = urlbits.pop()
        if bit.startswith(_('par-')):
            try:
                value = urlbits.pop()
            except IndexError:
                raise Http404
            if bit.endswith(_('categorie')):
                item = get_object_or_404(Category, slug=value)
                sqs = sqs.narrow("categories:%s" % value)
                breadcrumbs[bit] = { 'name':'categories', 'value':value, 'label':bit, 'object':item, 'pretty_name':_(u"Catégorie"), 'pretty_value':item.name, 'url':'par-%s/%s' % (bit, value), 'facet':True }
            elif bit.endswith(_('loueur')):
                item = get_object_or_404(Patron, slug=value)
                sqs = sqs.narrow("owner:%s" % value)
                breadcrumbs[bit] = { 'name':'owner', 'value':value, 'label':bit, 'object':item, 'pretty_name':_(u"Loueur"), 'pretty_value':item.username, 'url':'par-%s/%s' % (bit, value), 'facet':True }
            else:
                raise Http404
        elif bit.startswith(_('page')):
            try:
                page = urlbits.pop()
            except IndexError:
                raise Http404
        else:
            raise Http404
    form = FacetedSearchForm(dict((facet['name'], facet['value']) for facet in breadcrumbs.values()), searchqueryset=sqs)
    sqs = form.search()
    return object_list(request, sqs, page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name="products/product_list.html", template_object_name='product', extra_context={ 
        'facets':sqs.facet_counts(), 'form':form, 'breadcrumbs':breadcrumbs,
        'where':where, 'radius':radius, 'suggestions':suggestions, 'query':query,
        'urlbits':dict((facet['label'], facet['value']) for facet in breadcrumbs.values() if facet['facet'])
    })
