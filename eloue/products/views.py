# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.vary import vary_on_headers
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.views.decorators.csrf import csrf_exempt
from haystack.query import SearchQuerySet
from django.http import HttpResponse
from eloue.decorators import ownership_required, secure_required, mobify
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.products.forms import AlertSearchForm, FacetedSearchForm, ProductForm, ProductEditForm, AlertForm
from eloue.products.models import Category, Product, Curiosity, UNIT, Alert
from eloue.products.wizard import ProductWizard, AlertWizard, AlertAnswerWizard
from eloue.products.search_indexes import alert_search, product_search 
from django.views.decorators.http import require_POST, require_GET
import re
import redis

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
redis = redis.Redis(host='localhost', port=6379, db=0)

@mobify
@cache_page(300)
@vary_on_headers('Referer')
def homepage(request):
    curiosities = Curiosity.on_site.all()
    form = FacetedSearchForm()
    alerts = Alert.on_site.all()[:3]
    return direct_to_template(request, template='index.html', extra_context={'form': form, 'curiosities': curiosities, 'alerts':alerts})


@mobify
@cache_page(300)
def search(request):
    form = FacetedSearchForm()
    return direct_to_template(request, template='products/search.html', extra_context={'form': form})


@never_cache
@secure_required
def product_create(request, *args, **kwargs):
    wizard = ProductWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_edit(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)
    initial = {
        'category': product.category.id,
        'deposit_amount': product.deposit_amount
    }
    for price in product.prices.all():
        initial['%s_price' % UNIT.reverted[price.unit].lower()] = price.amount
    form = ProductEditForm(data=request.POST or None, files=request.FILES or None, instance=product, initial=initial)
    if form.is_valid():
        product = form.save()
        messages.success(request, _(u"Votre produit a bien été édité !"))
    return direct_to_template(request, 'products/product_edit.html', extra_context={'product': product, 'form': form})


@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_delete(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, _(u"Votre objet à bien été supprimée"))
        return redirect_to(request, reverse('owner_product'))
    else:
        return direct_to_template(request, template='products/product_delete.html', extra_context={'product': product})


@mobify
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
                breadcrumbs[bit] = {
                    'name': 'categories', 'value': value, 'label': bit, 'object': item,
                    'pretty_name': _(u"Catégorie"), 'pretty_value': item.name,
                    'url': 'par-%s/%s' % (bit, value), 'facet': True
                }
            elif bit.endswith(_('loueur')):
                item = get_object_or_404(Patron.on_site, slug=value)
                breadcrumbs[bit] = {
                    'name': 'owner', 'value': value, 'label': bit, 'object': item,
                    'pretty_name': _(u"Loueur"), 'pretty_value': item.username,
                    'url': 'par-%s/%s' % (bit, value), 'facet': True
                }
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
    return object_list(request, sqs, page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name="products/product_list.html",
        template_object_name='product', extra_context={
            'facets': sqs.facet_counts(), 'form': form, 'breadcrumbs': breadcrumbs, 'suggestions': suggestions,
            'urlbits': dict((facet['label'], facet['value']) for facet in breadcrumbs.values() if facet['facet'])
    })


@never_cache
@secure_required
def alert_create(request, *args, **kwargs):
    wizard = AlertWizard([AlertForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@cache_page(900)
@vary_on_cookie
def alert_list(request, sqs=SearchQuerySet(), page=None):
    form = FacetedSearchForm()
    search_alert_form = AlertSearchForm(request.GET, searchqueryset=sqs)
    return object_list(request, search_alert_form.search(), page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name="products/alert_list.html",
        template_object_name='alert', extra_context={'form': form, 'search_alert_form':search_alert_form})


@never_cache
@secure_required
def alert_inform(request, *args, **kwargs):
    wizard = AlertAnswerWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@login_required
def alert_inform_success(request, alert_id):
    return object_detail(request, queryset=Alert.objects.all(), object_id=alert_id,
        template_name='products/alert_unform_success.html', template_object_name='alert')


@login_required
def alert_delete(request, alert_id):
    alert = get_object_or_404(Alert, pk=alert_id)
    if request.method == "POST":
        alert.delete()
        messages.success(request, _(u"Votre alerte à bien été supprimée"))
        return redirect_to(request, reverse('alert_edit'))
    else:
        return direct_to_template(request, template='products/alert_delete.html', extra_context={'alert': alert})

def suggestion(request): 
    word = request.GET['q']
    resp = redis.get(word)
    #if resp:
    #    return HttpResponse(resp)
    results_categories = SearchQuerySet().filter(categories__startswith=word).models(Product)
    resp_list = []
    for result in results_categories:
        if len(result.categories)>1:
            for category in result.categories:
                if category.startswith(word):
                    if "-" in category:
                        resp_list.append(category.split("-")[0].lower())
                    else:
                        resp_list.append(category.lower())      
        else:
            category = result.categories[0]
            if category.startswith(word):
                if "-" in category:
                    resp_list.append(category.split("-")[0].lower())
                else:
                    resp_list.append(category.lower())
    results_description = SearchQuerySet().autocomplete(description=word)
    results_summary = SearchQuerySet().autocomplete(summary=word)
    for result in results_summary:
        for m in re.finditer(r"^%s(\w+)"%word, result.summary, re.I):
            resp_list.append(m.group(0).lower())
    for result in results_description:
        for m in re.finditer(r"^%s(\w+)"%word, result.description, re.I):
            resp_list.append(m.group(0).lower())
    resp_list = list(set(resp_list))
    print ">>>>>>resp_list>>>>>>", resp_list
    resp_list = resp_list[-10:]
    resp = ""
    for el in resp_list:
        resp += "\n%s"%el
    redis.set(word, resp)
    return HttpResponse(resp)
        
        