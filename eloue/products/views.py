# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list

from haystack.query import SearchQuerySet

from eloue.decorators import secure_required
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.products.forms import FacetedSearchForm, ProductForm
from eloue.products.models import Category
from eloue.products.wizard import ProductWizard

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


@cache_page(300)
def homepage(request):
    form = FacetedSearchForm()
    return direct_to_template(request, template='index.html', extra_context={'form': form})


@never_cache
@secure_required
def product_create(request, *args, **kwargs):
    wizard = ProductWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@cache_page(900)
@vary_on_cookie
def product_list(request, urlbits, sqs=SearchQuerySet(), suggestions=None, page=None):
    form = FacetedSearchForm(request.GET)
    if not form.is_valid():
        raise Http404
        
    breadcrumbs = SortedDict()
    breadcrumbs['q'] = {'name': 'q', 'value': form.cleaned_data.get('q', None), 'label': 'q', 'facet': False}
    breadcrumbs['l'] = {'name': 'l', 'value': form.cleaned_data.get('l', None), 'label': 'l', 'facet': False}
    breadcrumbs['r'] = {'name': 'r', 'value': form.cleaned_data.get('r', None), 'label': 'r', 'facet': False}
    breadcrumbs['sort'] = {'name': 'sort', 'value': form.cleaned_data.get('sort', None), 'label': 'sort', 'facet': False}
    
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
                breadcrumbs[bit] = {'name': 'categories', 'value': value, 'label': bit, 'object': item, 'pretty_name': _(u"Catégorie"), 'pretty_value': item.name, 'url': 'par-%s/%s' % (bit, value), 'facet': True}
            elif bit.endswith(_('loueur')):
                item = get_object_or_404(Patron, slug=value)
                sqs = sqs.narrow("owner:%s" % value)
                breadcrumbs[bit] = {'name': 'owner', 'value': value, 'label': bit, 'object': item, 'pretty_name': _(u"Loueur"), 'pretty_value': item.username, 'url': 'par-%s/%s' % (bit, value), 'facet': True}
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
    sqs, suggestions = form.search()
    return object_list(request, sqs, page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name="products/product_list.html", template_object_name='product', extra_context={
        'facets': sqs.facet_counts(), 'form': form, 'breadcrumbs': breadcrumbs, 'suggestions': suggestions,
        'urlbits': dict((facet['label'], facet['value']) for facet in breadcrumbs.values() if facet['facet'])
    })
