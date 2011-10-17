# -*- coding: utf-8 -*-
 # -*- coding: utf-8 -*-
import re
from urllib import urlencode
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict, MultiValueDict
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list
from django.db.models import Q

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_detail

from django.http import Http404, HttpResponseRedirect

from haystack.query import SearchQuerySet
from django.http import HttpResponse
from eloue.decorators import ownership_required, secure_required, mobify
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron

from eloue.products.forms import AlertSearchForm, AlertForm, FacetedSearchForm, ProductForm, ProductEditForm, MessageEditForm

from eloue.products.models import Category, Product, Curiosity, UNIT, ProductRelatedMessage, Alert, MessageThread
from eloue.products.wizard import ProductWizard, MessageWizard, AlertWizard, AlertAnswerWizard
from eloue.rent.forms import BookingOfferForm
from eloue.rent.models import Booking
from django_messages.forms import ComposeForm
from eloue.products.utils import format_quote, escape_percent_sign
from django.core.cache import cache
 

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

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


# @login_required
# def compose_product_related_message(request, recipient=None, form_class=MessageComposeForm,
#     template_name='django_messages/compose.html', success_url=None, recipient_filter=None):
#     if request.method == "POST":
#         sender = request.user
#         form = form_class(request.POST, recipient_filter=recipient_filter)
#         if form.is_valid():
#             form.save(sender=request.user)
#             messages.add_message(request, messages.SUCCESS, _(u"Message successfully sent."))
#             if success_url is None:
#                 success_url = reverse('messages_inbox')
#             if request.GET.has_key('next'):
#                 success_url = request.GET['next']
#             return HttpResponseRedirect(success_url)
#     else:
#         form = form_class()
#         if recipient is not None:
#             recipients = [u.username for u in User.objects.filter(username__in=[r.strip() for r in recipient.split('+')])]
#             form.fields['recipient'].initial = ','.join(recipients)
#     return render_to_response(template_name, {
#         'form': form,
#         }, context_instance=RequestContext(request))

@login_required
def threaded_inbox(request):
    thread_list = MessageThread.objects.filter(Q(sender=request.user)|Q(recipient=request.user)).order_by('-last_message__sent_at')
    return render_to_response('products/inbox.html', {'thread_list': thread_list})

@login_required
def thread_details(request, thread_id):

    thread = get_object_or_404(MessageThread, id=thread_id)
    user = request.user
    peer = thread.sender if user == thread.recipient else thread.recipient

    product = thread.product
    owner = product.owner
    borrower = user if peer == product.owner else peer
    if request.user != thread.sender and request.user != thread.recipient:
        return HttpResponseForbidden()
    
    message_list = thread.messages.order_by('sent_at')
    
    editForm = MessageEditForm(prefix='0')
    offerForm = BookingOfferForm(prefix='1')

    if request.method == "POST":
        editForm = MessageEditForm(request.POST, prefix='0')
        if editForm.is_valid():
            if editForm.cleaned_data['jointOffer']:
                booking = Booking(
                  product=product, 
                  owner=owner, 
                  borrower=borrower, 
                  state=Booking.STATE.UNACCEPTED,
                  ip=request.META.get('REMOTE_ADDR', None) if user==borrower else None) # we can fill out IP if the user is the borrower, else only when peer accepts the offer
                offerForm = BookingOfferForm(request.POST, instance=booking, prefix='1')
                if offerForm.is_valid():
                    messages_with_offer = message_list.filter(~Q(offer=None) & ~Q(offer__state=Booking.STATE.REJECTED))
                    for message in messages_with_offer:
                        message.offer.state = Booking.STATE.REJECTED
                        message.offer.save()
                    editForm.save(product, user, peer, parent_msg=thread.last_message, offer=offerForm.save())
                    messages.add_message(request, messages.SUCCESS, _(u"Message successfully sent with booking offer."))
                    return HttpResponseRedirect(reverse('thread_details', kwargs={'thread_id': thread_id}))
            else:
                editForm.save(product=product, sender=user, recipient=peer, parent_msg=thread.last_message)
                messages.add_message(request, messages.SUCCESS, _(u"Message successfully sent."))
                return HttpResponseRedirect(reverse('thread_details', kwargs={'thread_id': thread_id}))

    return render_to_response('products/message_view.html', {'message_list': message_list, 'editForm': editForm, 'offerForm': offerForm, 'Booking': Booking}, context_instance=RequestContext(request))

@login_required
def reply_product_related_message(request, message_id, form_class=MessageEditForm,
    template_name='django_messages/compose.html', success_url=None, recipient_filter=None,
    quote=format_quote):
    parent = get_object_or_404(ProductRelatedMessage, id=message_id)
    product = parent.product
    
    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404
    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST)
        if form.is_valid():
            form.save(product=product, sender=request.user, recipient=parent.sender, parent_msg=parent)
            messages.add_message(request, messages.SUCCESS, _(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class({
            'body': quote(parent.sender, parent.body),
            'subject': _(u"Re: %(subject)s") % {'subject': parent.subject},
            'recipient': parent.sender
            })
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@never_cache
@secure_required
def message_create(request, product_id, recipient_id):
    message_wizard = MessageWizard([MessageEditForm, EmailAuthenticationForm])
    return message_wizard(request, product_id, recipient_id)


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
                params = MultiValueDict((facet['label'], [unicode(facet['value']).encode('utf-8')]) for facet in breadcrumbs.values() if (not facet['facet']) and not (facet['label'] == 'r' and facet['value'] == DEFAULT_RADIUS)and not (facet['label'] == 'l' and facet['value'] == '') and not (facet['label'] == 'sort' and facet['value'] == '') and not (facet['label'] == 'q' and facet['value'] == ''))
                path = item.get_absolute_url()
                for bit in urlbits:
                    if bit.startswith(_('page')):
                        try:
                            page = urlbits.pop(0)
                            path = '%s/%s/%s' % (path, _(u'page'), page)
                        except IndexError:
                            raise Http404
                if any([value for key, value in params.iteritems()]):
                    path = '%s?%s' % (path, urlencode(params))
                return redirect_to(request, escape_percent_sign(path))
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
            value = bit
            item = get_object_or_404(Category, slug=value)
            ancestors_slug = item.get_ancertors_slug()
            breadcrumbs['categorie'] = {
                'name': 'categories', 'value': value, 'label': ancestors_slug, 'object': item,
                'pretty_name': _(u"Catégorie"), 'pretty_value': item.name,
                'url': item.get_absolute_url(), 'facet': True
            }
    
    site_url="%s://%s" % ("https" if USE_HTTPS else "http", Site.objects.get_current().domain)
    form = FacetedSearchForm(dict((facet['name'], facet['value']) for facet in breadcrumbs.values()), searchqueryset=sqs)
    sqs, suggestions = form.search()
    return object_list(request, sqs, page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name="products/product_list.html",
        template_object_name='product', extra_context={
            'facets': sqs.facet_counts(), 'form': form, 'breadcrumbs': breadcrumbs, 'suggestions': suggestions,
            'site_url': site_url
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
    cache_value = cache.get(word)
    if cache_value:
        return HttpResponse(cache_value)
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
    resp_list = resp_list[-10:]
    resp = ""
    for el in resp_list:
        resp += "\n%s"%el
    cache.set(word, resp, 0)
    return HttpResponse(resp)
        
        
