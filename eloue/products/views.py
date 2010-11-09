# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list

from haystack.query import SearchQuerySet

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.geocoder import Geocoder
from eloue.products.forms import FacetedSearchForm, ProductForm
from eloue.products.models import Product, Category
from eloue.products.wizard import ProductWizard
from eloue.rent.forms import BookingForm
from eloue.rent.models import Booking

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
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
    search_form = FacetedSearchForm()
    booking_form = BookingForm(prefix='0', instance=Booking(product=product, owner=product.owner), initial={
        'basket':True,
        'started_at':[datetime.date.today().strftime('%d/%m/%Y'), '08:00:00'],
        'ended_at':[(datetime.date.today() + datetime.timedelta(days=1)).strftime('%d/%m/%Y'), '19:00:00']
    })
    return direct_to_template(request, template='products/product_detail.html', extra_context={ 'product':product,
        'booking_form':booking_form, 'search_form':search_form})


@never_cache
def product_create(request, *args, **kwargs):
    wizard = ProductWizard([ProductForm,EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@cache_page(900)
@vary_on_cookie
def product_list(request, urlbits, sqs=SearchQuerySet(), suggestions=None, page=None):
    query = request.GET.get('q', None)
    if query:
        sqs = sqs.auto_query(query).highlight()
        suggestions = sqs.spelling_suggestion()
    
    where, radius = request.GET.get('where', DEFAULT_RADIUS), request.GET.get('radius', None)
    if where:
        lat, lon = Geocoder.geocode(where)
        sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
        
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
