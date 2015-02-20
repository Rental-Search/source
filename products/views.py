# -*- coding: utf-8 -*-
import re
from urllib import urlencode
import urllib
import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict, MultiValueDict
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, TemplateView, View
from django.db.models import Q, Count
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

from haystack.query import SearchQuerySet
from suds import WebFault

from accounts.forms import EmailAuthenticationForm
from accounts.models import Patron
from accounts.search import patron_search
from eloue.api.decorators import ignore_filters, list_link
from eloue.api.exceptions import ValidationException, ServerException, ServerErrorEnum

from products.forms import (
    AlertSearchForm, AlertForm, FacetedSearchForm, ProductFacetedSearchForm, ProductForm,
    RealEstateEditForm, CarProductEditForm, ProductEditForm,
    ProductAddressEditForm, ProductPhoneEditForm, ProductPriceEditForm, MessageEditForm,
)
from products.models import (
    Category, Product, Curiosity, ProductRelatedMessage, Alert, MessageThread,
    CarProduct, RealEstateProduct
)
from products.choices import UNIT, SORT, PRODUCT_TYPE
from products.wizard import ProductWizard, MessageWizard, AlertWizard, AlertAnswerWizard
from products.utils import format_quote, escape_percent_sign
from products.search import product_search, car_search, realestate_search, product_only_search

from rent.forms import BookingOfferForm
from rent.models import Booking, Comment
from rent.choices import BOOKING_STATE

from eloue.decorators import ownership_required, secure_required, mobify, cached
from eloue.utils import cache_key
from eloue.geocoder import GoogleGeocoder
from eloue.views import LoginRequiredMixin, SearchQuerySetMixin, BreadcrumbsMixin
from shipping import helpers
from shipping.models import ShippingPoint
from shipping.serializers import ShippingPointListParamsSerializer, PudoSerializer

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 12) # UI v3: changed from 10 to 12
PAGINATE_UNAVAILABILITY_PERIODS_BY = getattr(settings, 'PAGINATE_UNAVAILABILITY_PERIODS_BY', 31)
DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)
MAX_DISTANCE = 1541

def get_point_and_radius(coords, radius=None):
    """get_point_and_radius(coords, radius=None):
    A helper function which transforms provided coordinates into a gis.geos.Point object and validates radius.

    Input:
    - coords : coordinates of the center of the zone of interest, tuple or list;
               must contain (latitude, longitude) in strict order
    - radius : a radius of the zone of interests, numeric (int or float), or any 'False' value like None, False, empty sequences, etc.

    Output: a (point, radius) tuple where
    - point : gis.geos.Point object made from the input coordinates
    - radius : a validated radius of the zone of interests, numeric (int or float)
    """
    point = Point(*coords)
    radius = min(radius or float('inf'), MAX_DISTANCE)
    return point, radius

def get_last_added_sqs(search_index, location, sort_by_date='-created_at_date'):
    # only objects that are 'good' to be shown
    sqs = search_index.filter(is_good=1)

    # try to find products in the same region
    region_point, region_radius = get_point_and_radius(
        location['region_coords'] or location['coordinates'],
        location['region_radius'] or location['radius']
        )
    last_added = sqs.dwithin('location', region_point, Distance(km=region_radius)
        ).distance('location', region_point
        ).order_by(sort_by_date, SORT.NEAR)

    # if there are no products found in the same region
    if not last_added.count():
        # try to find products in the same country
        try:
            country_point, country_radius = get_point_and_radius(GoogleGeocoder().geocode(location['country'])[1:3])
        except:
            # silently ignore exceptions like country name is missing or incorrect
            pass
        else:
            last_added = sqs.dwithin('location', country_point, Distance(km=country_radius)
                ).distance('location', country_point
                ).order_by(sort_by_date, SORT.NEAR)

    # if there are no products found in the same country
    if not last_added.count():
        # do not filter on location, and return full list sorted by the provided date field only
        last_added = sqs.order_by(sort_by_date)

    return last_added


def last_added(search_index, location, offset=0, limit=PAGINATE_PRODUCTS_BY, sort_by_date='-created_at_date'):
    last_added = get_last_added_sqs(search_index, location, sort_by_date)
    return last_added[offset*limit:(offset+1)*limit]


def last_joined(*args, **kwargs):
    return last_added(*args, sort_by_date='-date_joined_date', **kwargs)

@mobify
def homepage(request):
    curiosities = Curiosity.on_site.all()
    location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
    address = location.get('formatted_address') or (u'{city}, {country}'.format(**location) if location.get('city') else u'{country}'.format(**location))
    form = FacetedSearchForm({'l': address}, auto_id='id_for_%s')
    alerts = Alert.on_site.all()[:3]
    categories_list = cache.get(cache_key('home_categories_list', Site.objects.get_current()))

    if categories_list is None:
        categories_list = {}
        parent_categories = Category.on_site.filter(parent__isnull=True).exclude(slug='divers')
        for cat in parent_categories:
            categories_list[cat] = list(cat.get_leafnodes().annotate(num_products=Count('products')).order_by('-num_products')[:5])
        cache.set(cache_key('home_categories_list', Site.objects.get_current()), categories_list, 10*60)

    return render_to_response(
        template_name='index.html', 
        dictionary={
            'product_list': last_added(product_only_search, location),
            'car_list': last_added(car_search, location),
            'realestate_list': last_added(realestate_search, location),
            'form': form, 'curiosities': curiosities,
            'alerts':alerts,
            'last_joined': last_joined(patron_search, location, limit=11),
            'categories_list': categories_list,
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
        content_type='text/plain; charset=utf-8'
    )


@mobify
@cache_page(300)
def search(request):
    form = FacetedSearchForm()
    return render(request, 'products/search.html', {'form': form})


@never_cache
@secure_required
def publish_new_ad(request, *args, **kwargs):
    if request.user.is_authenticated():
        if request.user.is_professional and not request.user.current_subscription:
            messages.success(request, _(u"En tant que professionnel, vous devez souscrire à un abonnement avant de pouvoir déposer une annonce."))
            return redirect(
                'accounts.views.patron_subscription'
            )
    return render(request, 'products/publish_new_ad.html')


@never_cache
@secure_required
def publish_new_ad2(request, *args, **kwargs):
    if request.user.is_authenticated():
        if request.user.is_professional and not request.user.current_subscription:
            messages.success(request, _(u"En tant que professionnel, vous devez souscrire à un abonnement avant de pouvoir déposer une annonce."))
            return redirect(
                'accounts.views.patron_subscription'
            )
    return render(request, 'products/publish_new_ad2.html')

    
@never_cache
@secure_required
def shipping_service_offer(request, *args, **kwargs):
    return render(request, 'products/shipping_service_offer.html')


@never_cache
@secure_required
def product_create(request, *args, **kwargs):
    wizard = ProductWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)

@never_cache
@secure_required
def car_product_create(request, *args, **kwargs):
    from products.forms import CarProductForm
    wizard = ProductWizard([CarProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)

@never_cache
@secure_required
def real_estate_product_create(request, *args, **kwargs):
    from products.forms import RealEstateForm
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
            'owner_product_edit', 
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
            messages.success(request, _(u"L'adresse a bien été modifiée"))
            return redirect(
                'owner_product_address_edit', 
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
def product_phone_edit(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)

    if request.method == "POST":
        form = ProductPhoneEditForm(data=request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, _(u"Le numéro de téléphone à bien été enregistré"))
            return redirect(
                'owner_product_phone_edit',
                slug=slug, product_id=product_id
            )
    else:
        form = ProductPhoneEditForm(instance=product)

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
            'owner_product_price_edit', 
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
    from products.forms import HighlightForm
    from products.models import ProductHighlight
    now = datetime.datetime.now()
    product = get_object_or_404(Product.on_site, pk=product_id)
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
    return render(
        request, 'products/product_highlight_edit.html', 
        {'product': product, 'old_highlights': old_highlights, 'form': form},
    )

@login_required
@ownership_required(model=Product, object_key='product_id', ownership=['owner'])
def product_top_position_edit(request, slug, product_id):
    from products.forms import TopPositionForm
    from products.models import ProductTopPosition
    now = datetime.datetime.now()
    product = get_object_or_404(Product.on_site, pk=product_id)
    old_toppositions = product.producttopposition_set.filter(ended_at__isnull=False).order_by('-ended_at')
    new_topposition = product.producttopposition_set.filter(ended_at__isnull=True)
    if new_topposition:
        topposition, = new_topposition
        if request.method == "POST":
            form = TopPositionForm(request.POST, instance=topposition)
            if form.is_valid():
                form.instance.ended_at = now
                form.save()
                return redirect('.')
        else:
            form = TopPositionForm(instance=topposition)
    else:
        if request.method == "POST":
            form = TopPositionForm(request.POST, instance=ProductTopPosition(product=product))
            if form.is_valid():
                form.save()
                return redirect('.')
        else:
            form = TopPositionForm(instance=ProductTopPosition(product=product))
    return render(
        request, 'products/product_top_position_edit.html',
        {'product': product, 'old_highlights': old_toppositions, 'form': form},
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
        return HttpResponseRedirect(reverse('inbox'))

    user = request.user
    peer = thread.sender if user == thread.recipient else thread.recipient
    product = thread.product
    owner = product.owner if product else None
    borrower = user if peer == owner else peer
    
    message_list = thread.messages.order_by('sent_at')

    if request.method == "POST":
        editForm = MessageEditForm(request.POST, prefix='0')
        if editForm.is_valid():
            if editForm.cleaned_data.get('jointOffer'): # FIXME: this is not used
                booking = Booking(
                  product=product, 
                  owner=owner, 
                  borrower=borrower, 
                  state=BOOKING_STATE.UNACCEPTED, # FIXME: direct manipulation of state could lead to FSM exception
                  ip=request.META.get('REMOTE_ADDR', None) if user==borrower else None) # we can fill out IP if the user is the borrower, else only when peer accepts the offer
                offerForm = BookingOfferForm(request.POST, instance=booking, prefix='1')
                if offerForm.is_valid():
                    messages_with_offer = message_list.filter(~Q(offer=None) & ~Q(offer__state=BOOKING_STATE.REJECTED)).select_related('offer').only('offer')
                    for message in messages_with_offer:
                        message.offer.reject()
                        message.offer.save()
                    editForm.save(product, user, peer, parent_msg=thread.last_message, offer=offerForm.save())
                    messages.add_message(request, messages.SUCCESS, _(u"Message successfully sent with booking offer."))
                    return HttpResponseRedirect(reverse('thread_details', kwargs={'thread_id': thread_id}))
            else:
                editForm.save(product=product, sender=user, recipient=peer, parent_msg=thread.last_message)
                messages.add_message(request, messages.SUCCESS, _(u"Message successfully sent."))
                return HttpResponseRedirect(reverse('thread_details', kwargs={'thread_id': thread_id}))
    elif request.method == "GET":
        editForm = MessageEditForm(prefix='0')
        offerForm = BookingOfferForm(prefix='1')
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

    if request.method == "POST":
        if product.bookings.all() or product.messages.all():
            product.is_archived = True
            product.save()
        else:
            product.delete()
        messages.success(request, _(u"Votre objet à bien été supprimée"))
        return redirect('owner_product')
    else:
        return render(request, 'products/product_delete.html', {'product': product})


class ProductList(SearchQuerySetMixin, BreadcrumbsMixin, ListView):
    template_name = "products/product_result.html"
    paginate_by = PAGINATE_PRODUCTS_BY
    context_object_name = 'product_list'

    @method_decorator(mobify)
    @method_decorator(cache_page(900))
    @method_decorator(vary_on_cookie)
    def dispatch(self, request, urlbits=None, sqs=SearchQuerySet().filter(is_archived=False), suggestions=None, page=None, **kwargs):
        self.breadcrumbs = self.get_breadcrumbs(request)
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
                        (facet['label'], [unicode(facet['value']).encode('utf-8')]) for facet in self.breadcrumbs.values() if is_facet_not_empty(facet)
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
                    return redirect(escape_percent_sign(path))
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
                self.breadcrumbs['categorie'] = {
                    'name': 'categories', 'value': value, 'label': ancestors_slug, 'object': item,
                    'pretty_name': _(u"Catégorie"), 'pretty_value': item.name,
                    'url': item.get_absolute_url(), 'facet': True
                }
        
        self.site_url="%s://%s" % ("https" if USE_HTTPS else "http", Site.objects.get_current().domain)
        self.form = self.form_class(
            dict((facet['name'], facet['value']) for facet in self.breadcrumbs.values()),
            searchqueryset=sqs
        )
        sqs, self.suggestions, self.top_products = self.form.search()
        # we use canonical_parameters to generate the canonical url in the header
        canonical_parameters = SortedDict(((key, unicode(value['value']).encode('utf-8')) for (key, value) in self.breadcrumbs.iteritems() if value['value']))
        canonical_parameters.pop('categorie', None)
        canonical_parameters.pop('r', None)
        canonical_parameters.pop('sort', None)
        canonical_parameters = urllib.urlencode(canonical_parameters)
        if canonical_parameters:
            canonical_parameters = '?' + canonical_parameters
        self.canonical_parameters = canonical_parameters
        self.kwargs.update({'page': page}) # Django 1.5+ ignore *args and **kwargs in View.dispatch()
        return super(ProductList, self).dispatch(request, sqs=sqs, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context.update({
            'facets': self.sqs.facet_counts(),
            'form': self.form,
            'breadcrumbs': self.breadcrumbs,
            'suggestions': self.suggestions,
            'site_url': self.site_url,
            'canonical_parameters': self.canonical_parameters,
            'top_products': self.top_products,
        })
        filter_limits = self.form.filter_limits
        if filter_limits:
            context.update(filter_limits)
        return context

@never_cache
@secure_required
def alert_create(request, *args, **kwargs):
    wizard = AlertWizard([AlertForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)

class AlertList(ListView):
    template_name = "products/alert_list.html"
    context_object_name = 'alert'

    @method_decorator(cache_page(900))
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return super(AlertList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AlertList, self).get_context_data(**kwargs)
        context['form'] = FacetedSearchForm()
        context['search_alert_form'] = self.search_alert_form
        return context

    def get_queryset(self):
        self.search_alert_form = AlertSearchForm(self.request.GET, searchqueryset=self.kwargs['sqs'])
        return self.search_alert_form

# @cache_page(900)
# @vary_on_cookie
# def alert_list(request, sqs=SearchQuerySet(), page=None):
#     form = FacetedSearchForm()
#     search_alert_form = AlertSearchForm(request.GET, searchqueryset=sqs)
#     return object_list(request, search_alert_form.search(), page=page, paginate_by=PAGINATE_PRODUCTS_BY, ,
#          extra_context={'form': form, 'search_alert_form':search_alert_form})


@never_cache
@secure_required
def alert_inform(request, *args, **kwargs):
    wizard = AlertAnswerWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)


class AlertInformSuccess(LoginRequiredMixin, DetailView):
    template_name = 'products/alert_unform_success.html'
    model = Alert
    context_object_name = 'alert'
    pk_url_kwarg = 'alert_id'


@login_required
def alert_delete(request, alert_id):
    alert = get_object_or_404(Alert, pk=alert_id)
    if request.method == "POST":
        alert.delete()
        messages.success(request, _(u"Votre alerte à bien été supprimée"))
        return redirect('alert_edit')
    else:
        return render(request, 'products/alert_delete.html', {'alert': alert})

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


# UI v3

from eloue.views import AjaxResponseMixin
from eloue.decorators import ajax_required
from products.forms import SuggestCategoryViewForm

class NavbarCategoryMixin(object):
    def get_context_data(self, **kwargs):
        category_list = list(Category.on_site.filter(pk__in=settings.NAVBAR_CATEGORIES))
        index = settings.NAVBAR_CATEGORIES.index
        category_list.sort(key=lambda obj: index(obj.pk))
        context = {
            'category_list': category_list,
        }
        context.update(super(NavbarCategoryMixin, self).get_context_data(**kwargs))
        return context

class PublishCategoryMixin(object):
    def get_context_data(self, **kwargs):
        context = dict()
        if settings.PUBLISH_CATEGORIES:
            context['publish_category_list'] = settings.PUBLISH_CATEGORIES
        context.update(super(PublishCategoryMixin, self).get_context_data(**kwargs))
        return context


class HomepageView(NavbarCategoryMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        product_list = last_added(product_search, self.location, limit=8)
        comment_list = Comment.objects.select_related(
            'booking__product__address'
        ).filter(
            booking__product__sites__id=settings.SITE_ID
        ).order_by('-created_at')

        context = {
            'product_list': product_list,
            'comment_list': comment_list,
            'products_on_site': Product.on_site.only('id'),
        }
        context.update(super(HomepageView, self).get_context_data(**kwargs))
        return context

    def get(self, request, *args, **kwargs):
        self.location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        return super(HomepageView, self).get(request, *args, **kwargs)


class ProductListView(ProductList):
    template_name = 'products/product_list.jade'
    form_class = ProductFacetedSearchForm

    def get_breadcrumbs(self, request):
        breadcrumbs = super(ProductListView, self).get_breadcrumbs(request)
        form = self.form
        #breadcrumbs['date_from'] = {'name': 'date_from', 'value': form.cleaned_data.get('date_from', None), 'label': 'date_from', 'facet': False}
        #breadcrumbs['date_to'] = {'name': 'date_to', 'value': form.cleaned_data.get('date_to', None), 'label': 'date_to', 'facet': False}
        breadcrumbs['price_from'] = {'name': 'price_from', 'value': form.cleaned_data.get('price_from', None), 'label': 'price_from', 'facet': False}
        breadcrumbs['price_to'] = {'name': 'price_to', 'value': form.cleaned_data.get('price_to', None), 'label': 'price_to', 'facet': False}
        breadcrumbs['categorie'] = {'name': 'categorie', 'value': None, 'label': 'categorie', 'facet': True}
        return breadcrumbs

    def get_context_data(self, **kwargs):
        if settings.FILTER_CATEGORIES:
            category_list = Category.on_site.filter(id__in=settings.FILTER_CATEGORIES)
        else:
            category_list = Category.on_site.filter(
                Q(parent__isnull=True) | ~Q(parent__sites__id=settings.SITE_ID)
            ).exclude(slug='divers')

        context = {
            'category_list': category_list
        }
        context.update(super(ProductListView, self).get_context_data(**kwargs))

        return context

class ProductDetailView(SearchQuerySetMixin, DetailView):
    model = Product
    template_name = 'products/_base_product_detail.jade'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # check if slug has changed
        product = self.object.object
        if product.slug != self.kwargs['slug']:
            return redirect(product, permanent=True)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        product = self.object.object
        if not product:
            raise Http404
        product_type = product.name
        comment_qs = Comment.borrowercomments.select_related('booking__borrower', 'booking_product').order_by('-created_at')
        # FIXME: It seems to be that `more_like_this` don't support filtration, but we need only products in response.
        # http://stackoverflow.com/questions/17537787/haystack-more-like-this-ignores-filters
        product_list = []
        chunk_size = 5
        i = 0
        while len(product_list) < 5:
            chunk = self.sqs.more_like_this(product)[i*chunk_size:(i+1)*chunk_size]
            if not chunk:
                break
            product_list.extend(filter(lambda x: x and isinstance(x.object, (Product, CarProduct, RealEstateProduct)), chunk))
            i += 1
        product_list = product_list[:5]

        product_comment_list = comment_qs.filter(booking__product=product)
        owner_comment_list = comment_qs.filter(booking__owner=product.owner)

        # FIXME: remove after mass rebuild of all images is done on hosting
        # from itertools import chain
        # from eloue.legacy import generate_patron_images, generate_picture_images
        # patron_set = set()
        # for picture in product.pictures.all():
            # generate_picture_images(picture)
        # for elem in product_list:
            # if elem.object:
                # patron_set.add(elem.object.owner)
                # for picture in elem.object.pictures.all()[:1]:
                    # generate_picture_images(picture, ['thumbnail', 'display'])
        # for comment in chain(product_comment_list, owner_comment_list):
            # patron_set.add(comment.booking.owner)
            # patron_set.add(comment.booking.borrower)
        # for patron in patron_set:
            # generate_patron_images(patron, ['product_page'])

        context = {
            'properties': product.properties.select_related('property'),
            'product_list': product_list,
            'product_comments': product_comment_list,
            'owner_comments': owner_comment_list,
            'product_type': product_type,
            'product_object': getattr(product, product_type) if product_type != 'product' else product,
            'insurance_available': settings.INSURANCE_AVAILABLE,
            'shipping_enabled': True,
        }
        context.update(super(ProductDetailView, self).get_context_data(**kwargs))
        return context

class PublishItemView(NavbarCategoryMixin, BreadcrumbsMixin, PublishCategoryMixin, TemplateView):
    template_name = 'publich_item/index.jade'

class SuggestCategoryView(AjaxResponseMixin, View):

    @method_decorator(ajax_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # search for products by provided query string
        form = SuggestCategoryViewForm(self.request.GET, searchqueryset=product_search)
        if not form.is_valid():
            return dict(errors=form.errors)

        sqs = form.search()

        # collect categories from product records found
        categories_set = reduce(lambda a, b: a.update(b.categories if b else []) or a, sqs, set())

        qs = Category.on_site.all()
        # we should filter by tree_id first because of SQL query performance benefits
        category = form.cleaned_data['category']
        if category is not None:
            qs = qs.filter(tree_id=category._mpttfield('tree_id'))
        qs = qs.filter(slug__in=categories_set)

        context = dict(categories=[
            [dict(id=c.id, name=c.name) for c in cat.get_ancestors(include_self=True)]
            for cat in qs if cat.is_leaf_node()
        ])
        return context


# REST API 2.0

from rest_framework.decorators import link, action
from rest_framework.response import Response
from rest_framework import status
import django_filters

from products import serializers, models
from products import filters as product_filters
from eloue.api import viewsets, filters, mixins, permissions
from rent.forms import Api20BookingForm
from rent.views import get_booking_price_from_form

class CategoryFilterSet(filters.FilterSet):
    parent__isnull = django_filters.Filter(name='parent', lookup_type='isnull')
    is_child_node = filters.MPTTBooleanFilter(lookup_type='is_child_node')
    is_leaf_node = filters.MPTTBooleanFilter(lookup_type='is_leaf_node')
    is_root_node = filters.MPTTBooleanFilter(lookup_type='is_root_node')

    class Meta:
        model = models.Category
        fields = ('parent', 'need_insurance')

class CategoryViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product categories to be viewed or edited.
    """
    permission_classes = (permissions.IsStaffOrReadOnly,)
    queryset = models.Category.on_site.select_related('description__title')
    serializer_class = serializers.CategorySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CategoryFilterSet
    ordering_fields = ('name',)
    public_actions = ('list', 'retrieve', 'ancestors', 'children', 'descendants')
    cache_control = {'max_age': 60*60} # categories are not going to change frequently

    @link()
    def ancestors(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_ancestors(), many=True)
        return Response(serializer.data)

    @link()
    def children(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_children(), many=True)
        return Response(serializer.data)

    @link()
    def descendants(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_descendants(), many=True)
        return Response(serializer.data)

class ProductFilterSet(filters.FilterSet):
    category__isdescendant = filters.MPTTModelFilter(name='categories', lookup_type='descendants', queryset=Category.objects.all())
    category = django_filters.ModelChoiceFilter(name='categories', queryset=Category.objects.all())

    class Meta:
        model = models.Product
        fields = ('deposit_amount', 'currency', 'address', 'is_archived', 'owner', 'created_at', 'quantity')

class ProductOrderingFilter(filters.OrderingFilter):

    def get_ordering(self, request):
        ordering = super(ProductOrderingFilter, self).get_ordering(request)
        if ordering:
            for i, param in enumerate(ordering):
                if 'category' in param:
                    ordering[i] = param.replace('category', 'categories__id')
        return ordering

class ProductViewSet(mixins.OwnerListPublicSearchMixin, mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.on_site.filter(is_archived=False).select_related('carproduct', 'realestateproduct', 'address', 'phone', 'category', 'owner')
    filter_backends = (product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'owner'
    search_index = product_search
    filter_class = ProductFilterSet
    ordering = '-created_at'
    ordering_fields = ('quantity', 'is_archived', 'category', 'created_at')
    haystack_ordering_fields = ('price', 'average_rate', 'distance')
    public_actions = ('retrieve', 'search', 'is_available',
                      'homepage', 'unavailability_periods')
    paginate_by = PAGINATE_PRODUCTS_BY

    navette = helpers.EloueNavette()

    _object = None

    # FIXME move to viewsets.ModelViewSet ??
    def get_object(self, queryset=None):
        if self._object is None:
            self._object = super(ProductViewSet, self
                    ).get_object(queryset=queryset)
        return self._object

    @link()
    def shipping_price(self, request, *args, **kwargs):
        params = serializers.ShippingPriceParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            product = self.get_object()
            try:
                departure_point = product.departure_point
            except ShippingPoint.DoesNotExist:
                raise ServerException({
                    'code': ServerErrorEnum.OTHER_ERROR[0],
                    'description': ServerErrorEnum.OTHER_ERROR[1],
                    'detail': _(u'Departure point not specified')
                })
            result = serializers.ShippingPriceSerializer(
                data=self.navette.get_shipping_price(departure_point.site_id, params['arrival_point_id']))
            if result.is_valid():
                return Response(result.data)

    @link()
    @ignore_filters([filters.DjangoFilterBackend])
    def shipping_points(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            departure_point = product.departure_point
        except ShippingPoint.DoesNotExist:
            raise ServerException({
                'code': ServerErrorEnum.OTHER_ERROR[0],
                'description': ServerErrorEnum.OTHER_ERROR[1],
                'detail': _(u'Departure point not specified')
            })

        params = ShippingPointListParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            lat = params['lat']
            lng = params['lng']
            if lat is None or lng is None:
                lat, lng = helpers.get_position(params['address'])
                if not all((lat, lng)):
                    return Response([])
            shipping_points = self.navette.get_shipping_points(lat, lng, params['search_type'])
            for shipping_point in shipping_points:
                # FIXME: could there be a depot without site_id?
                if 'site_id' in shipping_point:
                    try:
                        price = self.navette.get_shipping_price(departure_point.site_id, shipping_point['site_id'])
                    except WebFault:
                        shipping_points.remove(shipping_point)
                    else:
                        price['price'] *= 2
                        shipping_point.update(price)
                        # shipping_point.update({'price': 3.99})
            result = PudoSerializer(data=shipping_points, many=True)
            if result.is_valid():
                return Response(result.data)
        return Response([])

    @link()
    @ignore_filters([product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend])
    def is_available(self, request, *args, **kwargs):
        obj = self.get_object()

        form = Api20BookingForm(data=request.GET, instance=Booking(product=obj))
        res = get_booking_price_from_form(form)

        # add errors if the form is invalid
        if not form.is_valid():
            res['errors'] = form.errors
            return Response(res, status=400)

        return Response(res)

    @link()
    @ignore_filters([product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend])
    def unavailability(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = serializers.ListUnavailabilityPeriodSerializer(
                        data=request.QUERY_PARAMS,
                        context={'request': request},
                        instance=product)
        if not serializer.is_valid():
            raise ValidationException(serializer.errors)

        return Response(serializer.data)

    @link()
    @ignore_filters([product_filters.ProductHaystackSearchFilter, filters.DjangoFilterBackend])
    def unavailability_periods(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = serializers.MixUnavailabilityPeriodSerializer(
                context={'request': request, 'product': product},
                data=[request.QUERY_PARAMS,],
                many=True
        )

        if not serializer.is_valid():
            raise ValidationException(serializer.errors)

        self.object_list = serializer.context['object']
        self.paginate_by = PAGINATE_UNAVAILABILITY_PERIODS_BY
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = serializers.MixUnavailabilityPeriodPaginatedSerializer(
                    page,
                    context={'request': request, 'product': product}
            )

        return Response(serializer.data)

    @list_link()
    @ignore_filters([filters.HaystackSearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter])
    def homepage(self, request, *args, **kwargs):
        # get product ids from the search index
        location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        self.object_list = get_last_added_sqs(self.search_index, location)

        # we need to transform Haystack's SearchQuerySet to Django's QuerySet
        # TODO: it may be better to provide a custom Serializer which would support both
        def sqs_to_qs(sqs):
            pks = [obj.pk for obj in sqs]
            qs = self.get_queryset().filter(id__in=pks)
            return qs

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            page.object_list = sqs_to_qs(page.object_list)
            serializer = self.get_pagination_serializer(page)
        else:
            self.object_list = sqs_to_qs(self.object_list)
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)

    @link()
    def stats(self, request, *args, **kwargs):
        return Response(self.get_object().stats)

    @link()
    def absolute_url(self, request, *args, **kwargs):
        obj = self.get_object()
        return Response(dict(url=obj.get_absolute_url()))

    @cached_property
    def _category_from_native(self):
        return self.serializer_class().fields['category'].from_native

    def get_serializer_class(self):
        data = getattr(self, '_post_data', None)
        if data is not None:
            delattr(self, '_post_data')
            category = data.get('category', None)
            if category is not None:
                category = self._category_from_native(category)
                category = getattr(category, category._mptt_meta.tree_id_attr)
            if category == PRODUCT_TYPE.CAR or 'brand' in data:
                # we have CarProduct here
                return serializers.CarProductSerializer
            elif category == PRODUCT_TYPE.REALESTATE or 'private_life' in data:
                # we have RealEstateProduct here
                return serializers.RealEstateProductSerializer
        instance = getattr(self, 'object', None)
        if instance is not None:
            if hasattr(instance, 'carproduct'):
                # we have CarProduct here
                return serializers.CarProductSerializer
            elif hasattr(instance, 'realestateproduct'):
                # we have RealEstateProduct here
                return serializers.RealEstateProductSerializer
        return super(ProductViewSet, self).get_serializer_class()

    def get_serializer(self, instance=None, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        
        We should use different Seializer classes for instances of
        Product, CarProduct and RealEstateProduct models
        """
        if instance is not None:
            if hasattr(instance, 'carproduct'):
                # we have CarProduct here
                self.object = instance = instance.carproduct
            elif hasattr(instance, 'realestateproduct'):
                # we have RealEstateProduct here
                self.object = instance = instance.realestateproduct
        return super(ProductViewSet, self).get_serializer(instance=instance, **kwargs)

    def create(self, request, *args, **kwargs):
        self._post_data = request.DATA
        return super(ProductViewSet, self).create(request, *args, **kwargs)

    def get_location_url(self):
        return reverse('product-detail', args=(self.object.pk,))

class PriceViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product prices to be viewed or edited.
    """
    model = models.Price
    serializer_class = serializers.PriceSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'product__owner'
    filter_fields = ('product', 'unit')
    ordering_fields = ('name', 'amount')
    public_actions = ('retrieve',)

class UnavailabilityPeriodViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product unavailability periods to be viewed or edited.
    """
    model = models.UnavailabilityPeriod
    serializer_class = serializers.UnavailabilityPeriodSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, )
    owner_field = 'product__owner'
    filter_fields = ('product', )
    public_actions = ('list', 'retrieve')

class PictureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product images to be viewed or edited.
    """
    model = models.Picture
    serializer_class = serializers.PictureSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'product__owner'
    filter_fields = ('product', 'created_at')
    ordering_fields = ('created_at',)
    public_actions = ('retrieve',)

class CuriosityViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product curiosities to be viewed or edited.
    """
    queryset = models.Curiosity.on_site.all()
    serializer_class = serializers.CuriositySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('product',) # TODO: 'city', 'price')
    # TODO: ordering_fields = ('price',)
    public_actions = ('retrieve', 'list', )

class MessageThreadFilterSet(filters.FilterSet):
    participant = filters.MultiFieldFilter(name=('sender', 'recipient'))
    empty = django_filters.BooleanFilter(name='last_message__isnull')

    class Meta:
        model = models.MessageThread
        fields = ('sender', 'recipient', 'product')


class SetMessageOwnerMixin(mixins.SetOwnerMixin):
    def pre_save(self, obj):
        # set owner only for new messages threads
        if obj.id:
            return super(mixins.SetOwnerMixin, self).pre_save(obj)
        return super(SetMessageOwnerMixin, self).pre_save(obj)


class MessageThreadViewSet(SetMessageOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows message threads to be viewed or edited.
    """
    model = models.MessageThread
    queryset = models.MessageThread.objects.prefetch_related('messages').select_related('last_message')
    serializer_class = serializers.MessageThreadSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.RelatedOrderingFilter)
    owner_field = ('sender', 'recipient')
    filter_class = MessageThreadFilterSet
    ordering_fields = ('last_message__sent_at', 'last_message__read_at', 'last_message__replied_at')

class ProductRelatedMessageViewSet(SetMessageOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows product related messages to be viewed or edited.
    """
    model = models.ProductRelatedMessage
    serializer_class = serializers.ProductRelatedMessageSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = ('sender', 'recipient')
    filter_fields = ('thread', 'sender', 'recipient', 'offer')
    ordering_fields = ('sent_at',)

    def pre_save(self, obj):
        if not obj.subject and obj.thread:
            obj.subject = obj.thread.subject
        return super(ProductRelatedMessageViewSet, self).pre_save(obj)

    @action(methods=['put'])
    @ignore_filters([filters.DjangoFilterBackend])
    def seen(self, request, *args, **kwargs):
        message = self.get_object()
        if not message.read_at and message.recipient.id == request.user.id:
            message.read_at = datetime.datetime.now()
            message.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
