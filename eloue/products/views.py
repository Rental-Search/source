# -*- coding: utf-8 -*-
import re
from urllib import urlencode
import urllib
import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict, MultiValueDict
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list
from django.db.models import Q

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic.list_detail import object_detail

from django.http import Http404, HttpResponseRedirect

from haystack.query import SearchQuerySet
from django.http import HttpResponse
from eloue.decorators import ownership_required, secure_required, mobify
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron

from eloue.products.forms import AlertSearchForm, AlertForm, FacetedSearchForm, RealEstateEditForm, ProductForm, CarProductEditForm, ProductEditForm, ProductAddressEditForm, ProductPriceEditForm, MessageEditForm

from eloue.products.models import Category, Product, Curiosity, UNIT, ProductRelatedMessage, Alert, MessageThread
from eloue.accounts.models import Address

from eloue.products.wizard import ProductWizard, MessageWizard, AlertWizard, AlertAnswerWizard
from eloue.products.search_indexes import product_search, car_search, realestate_search, product_only_search
from eloue.rent.forms import BookingOfferForm
from eloue.rent.models import Booking
from django_messages.forms import ComposeForm
from eloue.products.utils import format_quote, escape_percent_sign
from django.core.cache import cache
 
from eloue.accounts.search_indexes import patron_search

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

def last_added(search_index, location, offset=0):
    coords = location['coordinates']
    region_coords = location.get('region_coords') or coords
    region_radius = location.get('region_radius') or location['radius']
    last_added = search_index.spatial(
            lat=region_coords[0], long=region_coords[1], radius=min(region_radius, 1541)
        ).spatial(
            lat=coords[0], long=coords[1], radius=min(region_radius*2 if region_radius else float('inf'), 1541)
        ).order_by('-created_at_date', 'geo_distance')
    return last_added[offset*10:(offset+1)*10]

@mobify
@cache_page(300, key_prefix=settings.CACHE_MIDDLEWARE_KEY_PREFIX)
def homepage(request):
    curiosities = Curiosity.on_site.all()
    location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
    address = location.get('formatted_address') or (u'{city}, {country}'.format(**location) if location.get('city') else u'{country}'.format(**location))
    form = FacetedSearchForm({'l': address}, auto_id='id_for_%s')
    alerts = Alert.on_site.all()[:3]
    try:
        coords = location['coordinates']
        last_joined = patron_search.spatial(
            lat=coords[0], long=coords[1], radius=1541
        ).order_by('-date_joined_date', 'geo_distance')
    except KeyError:
        last_joined = patron_search.order_by('-date_joined_date')
    return render_to_response(
        template_name='index.html', 
        dictionary={
            'product_list': last_added(product_only_search, location),
            'car_list': last_added(car_search, location),
            'realestate_list': last_added(realestate_search, location),
            'form': form, 'curiosities': curiosities,
            'alerts':alerts,
            'last_joined': last_joined[:11],
        }, 
        context_instance=RequestContext(request)
    )

def homepage_object_list(request, search_index, offset=0):
    offset = int(offset) if offset else 0
    location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
    return render_to_response(
        template_name='products/partials/result_list.html',
        dictionary={
            'product_list': last_added(search_index, location, offset),
            'truncation': 28
        },
        context_instance=RequestContext(request),
        mimetype='text/plain; charset=utf-8'
    )


@mobify
@cache_page(300)
def search(request):
    form = FacetedSearchForm()
    return direct_to_template(
        request, template='products/search.html', 
        extra_context={'form': form, }
    )


@never_cache
@secure_required
def publish_new_ad(request, *args, **kwargs):
    return direct_to_template(request, template='products/publish_new_ad.html')
    



@never_cache
@secure_required
def product_create(request, *args, **kwargs):
    wizard = ProductWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)

@never_cache
@secure_required
def car_product_create(request, *args, **kwargs):
    from eloue.products.forms import CarProductForm
    wizard = ProductWizard([CarProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)

@never_cache
@secure_required
def real_estate_product_create(request, *args, **kwargs):
    from eloue.products.forms import RealEstateForm
    wizard = ProductWizard([RealEstateForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_edit(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)
    try:
        form = CarProductEditForm(data=request.POST or None, files=request.FILES or None, instance=product.carproduct)
    except Product.DoesNotExist:
        try:
            form = RealEstateEditForm(data=request.POST or None, files=request.FILES or None, instance=product.realestateproduct)
        except Product.DoesNotExist:
            form = ProductEditForm(data=request.POST or None, files=request.FILES or None, instance=product)

    if form.is_valid():
        product = form.save()
        messages.success(request, _(u"Les modifications ont bien été prises en compte"))
        return redirect(
            'eloue.products.views.product_edit', 
            slug=slug, product_id=product_id
        )

    return render_to_response(
        'products/product_edit.html', dictionary={
            'product': product, 
            'form': form,
        }, 
        context_instance=RequestContext(request)
    )


@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_address_edit(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)

    if request.method == "POST":
        form = ProductAddressEditForm(data=request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, _(u"L'adress a bien été modifié"))
            return redirect(
                'eloue.products.views.product_address_edit', 
                slug=slug, product_id=product_id
            )
    else:
        form = ProductAddressEditForm(instance=product)
    
    
    return render_to_response(
        'products/product_edit.html', dictionary={
            'product': product, 
            'form': form
        }, 
        context_instance=RequestContext(request)
    )

@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_price_edit(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)
    initial = {}

    for price in product.prices.all():
        initial['%s_price' % UNIT.reverted[price.unit].lower()] = price.amount

    form = ProductPriceEditForm(data=request.POST or None, instance=product, initial=initial)

    if form.is_valid():
        product = form.save()
        messages.success(request, _(u"Les prix ont bien été modifiés"))
        return redirect(
            'eloue.products.views.product_price_edit', 
            slug=slug, product_id=product_id
        )
    return render_to_response(
        'products/product_edit.html', dictionary={
            'product': product, 
            'form': form
        }, 
        context_instance=RequestContext(request)
    )


@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_highlight_edit(request, slug, product_id):
    from eloue.products.forms import HighlightForm
    from eloue.products.models import ProductHighlight
    now = datetime.datetime.now()
    product = get_object_or_404(Product.on_site, pk=product_id)
    highlights = product.producthighlight_set.order_by('-ended_at')
    old_highlights = product.producthighlight_set.filter(ended_at__isnull=False).order_by('-ended_at')
    new_highlight = product.producthighlight_set.filter(ended_at__isnull=True)
    if new_highlight:
        highlight, = new_highlight
        if request.method == "POST":
            form = HighlightForm(request.POST, instance=highlight)
            if form.is_valid():
                form.instance.ended_at = now
                form.save()
                return redirect('.')
        else:
            form = HighlightForm(instance=highlight)
    else:
        if request.method == "POST":
            form = HighlightForm(request.POST, instance=ProductHighlight(product=product))
            if form.is_valid():
                form.save()
                return redirect('.')
        else:
            form = HighlightForm(instance=ProductHighlight(product=product))
    return render_to_response(
        'products/product_highlight_edit.html', 
        {'product': product, 'old_highlights': old_highlights, 'form': form},
        context_instance=RequestContext(request)
    )


def thread_list(user, is_archived):
    return sorted(
        MessageThread.objects.filter(
            Q(sender=user, sender_archived=is_archived)
            |Q(recipient=user, recipient_archived=is_archived)
        ).order_by('-last_message__sent_at'), 
        key=lambda thread: not (thread.new_sender() if user==thread.sender else thread.new_recipient())
    )


@login_required
def inbox(request):
    user = request.user
    threads = thread_list(user, False)
    return render_to_response(
      'products/inbox.html', 
      {'thread_list': threads}, 
      context_instance=RequestContext(request)
    )

@login_required
def archived(request):
    user = request.user
    threads = thread_list(user, True)
    return render_to_response(
      'products/archives.html', 
      {'thread_list': threads}, 
      context_instance=RequestContext(request)
    )

@login_required
def archive_thread(request, thread_id):
    thread = get_object_or_404(MessageThread, pk=thread_id)
    if thread.sender != request.user and thread.recipient != request.user:
        return HttpResponseForbidden()
    if request.user == thread.sender:
        thread.sender_archived = True
    else:
        thread.recipient_archived = True
    thread.save()
    return HttpResponseRedirect(reverse('inbox'))

@login_required
def unarchive_thread(request, thread_id):
    thread = get_object_or_404(MessageThread, pk=thread_id)
    if thread.sender != request.user and thread.recipient != request.user:
        return HttpResponseForbidden()
    if request.user == thread.sender:
        thread.sender_archived = False
    else:
        thread.recipient_archived = False
    thread.save()
    return HttpResponseRedirect(reverse('archived'))

@login_required
def thread_details(request, thread_id):

    thread = get_object_or_404(MessageThread, id=thread_id)
    if request.user != thread.sender and request.user != thread.recipient:
        return HttpResponseForbidden()

    user = request.user
    peer = thread.sender if user == thread.recipient else thread.recipient
    product = thread.product
    owner = product.owner if product else None
    borrower = user if peer == owner else peer
    
    message_list = thread.messages.order_by('sent_at')
    
    editForm = MessageEditForm(prefix='0')
    offerForm = BookingOfferForm(prefix='1')

    if request.method == "POST":
        editForm = MessageEditForm(request.POST, prefix='0')
        if editForm.is_valid():
            if editForm.cleaned_data.get('jointOffer'):
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
    elif request.method == "GET":
        for message in message_list.filter(recipient=user, read_at=None):
            message.read_at = datetime.datetime.now()
            message.save()
    return render_to_response('products/message_view.html', {'thread': thread, 'message_list': message_list, 'editForm': editForm, 'offerForm': offerForm, 'Booking': Booking}, context_instance=RequestContext(request))

@login_required
def reply_product_related_message(request, message_id, form_class=MessageEditForm,
    template_name='django_messages/compose.html', success_url=None, recipient_filter=None,
    quote=format_quote):
    parent = get_object_or_404(ProductRelatedMessage, id=message_id)
    product = parent.product
    
    if parent.sender != request.user and parent.recipient != request.user:
        return HttpResponseForbidden()
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

@never_cache
@secure_required
def patron_message_create(request, recipient_username):
    message_wizard = MessageWizard([MessageEditForm, EmailAuthenticationForm])
    recipient = Patron.objects.get(slug=recipient_username)
    return message_wizard(request, None, recipient.pk)

@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_delete(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id).subtype

    if product.bookings.all():
        is_booked = True
    else:
        is_booked = False

    if request.method == "POST":
        product.delete()
        messages.success(request, _(u"Votre objet à bien été supprimée"))
        return redirect_to(request, reverse('owner_product'))
    else:
        return direct_to_template(request, template='products/product_delete.html', extra_context={'product': product, 'is_booked': is_booked})


@mobify
@cache_page(900)
@vary_on_cookie
def product_list(request, urlbits, sqs=SearchQuerySet(), suggestions=None, page=None):
    location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
    query_data = request.GET.copy()
    if not query_data.get('l'):
        query_data['l'] = location['country']
    form = FacetedSearchForm(query_data)
    if not form.is_valid():
        raise Http404
    
    breadcrumbs = SortedDict()
    breadcrumbs['q'] = {'name': 'q', 'value': form.cleaned_data.get('q', None), 'label': 'q', 'facet': False}
    breadcrumbs['sort'] = {'name': 'sort', 'value': form.cleaned_data.get('sort', None), 'label': 'sort', 'facet': False}
    breadcrumbs['l'] = {'name': 'l', 'value': form.cleaned_data.get('l', None), 'label': 'l', 'facet': False}
    breadcrumbs['r'] = {'name': 'r', 'value': form.cleaned_data.get('r', None), 'label': 'r', 'facet': False}
    breadcrumbs['renter'] = {'name': 'renter', 'value': form.cleaned_data.get('renter'), 'label': 'renter', 'facet': False}

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
                is_facet_not_empty = lambda facet: not (
                    facet['facet'] or
                    (facet['label'], facet['value']) in [ ('sort', ''), ('q', '')]
                )
                params = MultiValueDict(
                    (facet['label'], [unicode(facet['value']).encode('utf-8')]) for facet in breadcrumbs.values() if is_facet_not_empty(facet)
                )
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
    form = FacetedSearchForm(
        dict((facet['name'], facet['value']) for facet in breadcrumbs.values()),
        searchqueryset=sqs)
    sqs, suggestions = form.search()
    # we use canonical_parameters to generate the canonical url in the header
    canonical_parameters = SortedDict(((key, unicode(value['value']).encode('utf-8')) for (key, value) in breadcrumbs.iteritems() if value['value']))
    canonical_parameters.pop('categorie', None)
    canonical_parameters.pop('r', None)
    canonical_parameters.pop('sort', None)
    canonical_parameters = urllib.urlencode(canonical_parameters)
    if canonical_parameters:
        canonical_parameters = '?' + canonical_parameters
    return object_list(request, sqs, page=page, paginate_by=PAGINATE_PRODUCTS_BY, template_name="products/product_result.html",
        template_object_name='product', extra_context={
            'facets': sqs.facet_counts(), 'form': form, 'breadcrumbs': breadcrumbs, 'suggestions': suggestions,
            'site_url': site_url, 'canonical_parameters': canonical_parameters
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
