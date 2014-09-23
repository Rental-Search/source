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
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count, Avg
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

from haystack.query import SearchQuerySet
from haystack.constants import DJANGO_ID

from accounts.forms import EmailAuthenticationForm
from accounts.models import Patron
from accounts.search import patron_search

from products.forms import AlertSearchForm, AlertForm, FacetedSearchForm, RealEstateEditForm, ProductForm, CarProductEditForm, ProductEditForm, ProductAddressEditForm, ProductPhoneEditForm, ProductPriceEditForm, MessageEditForm
from products.models import Category, Product, Curiosity, ProductRelatedMessage, Alert, MessageThread
from products.choices import UNIT, SORT
from products.wizard import ProductWizard, MessageWizard, AlertWizard, AlertAnswerWizard
from products.utils import format_quote, escape_percent_sign
from products.search import product_search, car_search, realestate_search, product_only_search

from rent.forms import BookingOfferForm
from rent.models import Booking
from rent.choices import BOOKING_STATE

from eloue.decorators import ownership_required, secure_required, mobify, cached
from eloue.utils import cache_key
from eloue.geocoder import GoogleGeocoder
from eloue.views import LoginRequiredMixin

PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 12) # UI v3: changed from 10 to 12
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

def last_added(search_index, location, offset=0, limit=PAGINATE_PRODUCTS_BY, sort_by_date='-created_at_date'):
    # try to find products in the same region
    region_point, region_radius = get_point_and_radius(
        location['region_coords'] or location['coordinates'],
        location['region_radius'] or location['radius']
        )
    last_added = search_index.dwithin('location', region_point, Distance(km=region_radius)
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
            last_added = search_index.dwithin('location', country_point, Distance(km=country_radius)
                ).distance('location', country_point
                ).order_by(sort_by_date, SORT.NEAR)

    # if there are no products found in the same country
    if not last_added.count():
        # do not filter on location, and return full list sorted by the provided date field only
        last_added = search_index.order_by(sort_by_date)

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


class ProductList(ListView):
    template_name = "products/product_result.html"
    paginate_by = PAGINATE_PRODUCTS_BY
    context_object_name = 'product_list'

    @method_decorator(mobify)
    @method_decorator(cache_page(900))
    @method_decorator(vary_on_cookie)
    def dispatch(self, request, urlbits=None, sqs=SearchQuerySet(), suggestions=None, page=None):
        location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        query_data = request.GET.copy()
        if not query_data.get('l'):
            query_data['l'] = location['country']
        form = FacetedSearchForm(query_data)
        if not form.is_valid():
            raise Http404
        
        self.breadcrumbs = SortedDict()
        self.breadcrumbs['q'] = {'name': 'q', 'value': form.cleaned_data.get('q', None), 'label': 'q', 'facet': False}
        self.breadcrumbs['sort'] = {'name': 'sort', 'value': form.cleaned_data.get('sort', None), 'label': 'sort', 'facet': False}
        self.breadcrumbs['l'] = {'name': 'l', 'value': form.cleaned_data.get('l', None), 'label': 'l', 'facet': False}
        self.breadcrumbs['r'] = {'name': 'r', 'value': form.cleaned_data.get('r', None), 'label': 'r', 'facet': False}
        self.breadcrumbs['renter'] = {'name': 'renter', 'value': form.cleaned_data.get('renter'), 'label': 'renter', 'facet': False}

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
        self.form = FacetedSearchForm(
            dict((facet['name'], facet['value']) for facet in self.breadcrumbs.values()),
            searchqueryset=sqs)
        self.sqs, self.suggestions, self.top_products = self.form.search()
        # we use canonical_parameters to generate the canonical url in the header
        self.canonical_parameters = SortedDict(((key, unicode(value['value']).encode('utf-8')) for (key, value) in self.breadcrumbs.iteritems() if value['value']))
        self.canonical_parameters.pop('categorie', None)
        self.canonical_parameters.pop('r', None)
        self.canonical_parameters.pop('sort', None)
        self.canonical_parameters = urllib.urlencode(self.canonical_parameters)
        if self.canonical_parameters:
            self.canonical_parameters = '?' + self.canonical_parameters
        self.kwargs.update({'page': page}) # Django 1.5+ ignore *args and **kwargs in View.dispatch()
        return super(ProductList, self).dispatch(request, urlbits, sqs, suggestions, page=page)

    def get_queryset(self):
        return self.sqs

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['facets'] = self.sqs.facet_counts()
        context['form'] = self.form
        context['breadcrumbs'] = self.breadcrumbs
        context['suggestions'] = self.suggestions
        context['site_url'] = self.site_url
        context['canonical_parameters'] = self.canonical_parameters
        context['top_products'] = self.top_products
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

class HomepageView(TemplateView):
    template_name = 'index.jade'
    breadcrumbs = {'sort': {'name': 'sort', 'value': '', 'label': 'sort', 'facet': False}}

    @property
    @cached(10*60)
    def home_context(self):
        product_stats = Product.objects.extra(
            tables=['accounts_address'],
            where=['"products_product"."address_id" = "accounts_address"."id"'],
            select={'city': 'lower(accounts_address.city)'}
        ).values('city').annotate(Count('id')).order_by('-id__count')
        return {
            'cities_list': product_stats,
            'total_products': Product.objects.only('id').count(),
            'categories_list': Category.on_site.filter(parent__isnull=True).exclude(slug='divers'),
            'product_list': last_added(product_search, self.location, limit=8),
            'breadcrumbs': self.breadcrumbs,
        }

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        context.update(self.home_context)
        return context

    def get(self, request, *args, **kwargs):
        self.location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        return super(HomepageView, self).get(request, *args, **kwargs)

class ProductListView(ProductList):
    template_name = 'products/product_list.jade'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.jade'
    context_object_name = 'product'

    def dispatch(self, request, *args, **kwargs):
        self.sqs = kwargs.get('sqs', SearchQuerySet())
        return super(ProductDetailView, self).dispatch(request, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # check if slug has changed
        product = self.object.object
        if product.slug != self.kwargs['slug']:
            return redirect(product, permanent=True)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_queryset(self):
        return self.sqs.load_all()

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(**{DJANGO_ID: pk})

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.best_match()
        except IndexError:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})
        return obj


# REST API 2.0

from rest_framework import response
from rest_framework.decorators import link
import django_filters

from products import serializers, models
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

class CategoryViewSet(viewsets.ReadOnlyModelViewSet): # FIXME: change to NonDeletableModelViewSet after merging Category and CategoryDescription
    """
    API endpoint that allows product categories to be viewed or edited.
    """
    permission_classes = (permissions.IsStaffOrReadOnly,)
    queryset = models.Category.on_site.select_related('description__title')
    serializer_class = serializers.CategorySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CategoryFilterSet
    ordering_fields = ('name',)

    @link()
    def ancestors(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_ancestors(), many=True)
        return response.Response(serializer.data)

    @link()
    def children(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_children(), many=True)
        return response.Response(serializer.data)

    @link()
    def descendants(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj.get_descendants(), many=True)
        return response.Response(serializer.data)

class ProductFilterSet(filters.FilterSet):
    category__isdescendant = filters.MPTTModelFilter(name='category', lookup_type='descendants', queryset=Category.objects.all())

    class Meta:
        model = models.Product
        fields = ('deposit_amount', 'currency', 'address', 'quantity', 'is_archived', 'category', 'owner', 'created_at')

class ProductViewSet(mixins.OwnerListPublicSearchMixin, mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.on_site.select_related('carproduct', 'realestateproduct', 'address', 'phone', 'category', 'owner')
    filter_backends = (filters.HaystackSearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'owner'
    search_index = product_search
    filter_class = ProductFilterSet
    ordering_fields = ('quantity', 'is_archived', 'category')

    @link()
    def is_available(self, request, *args, **kwargs):
        obj = self.get_object()

        form = Api20BookingForm(data=request.GET, instance=Booking(product=obj))
        res = get_booking_price_from_form(form)

        # add errors if the form is invalid
        if not form.is_valid():
            res['errors'] = form.errors
            return response.Response(res, status=400)

        return response.Response(res)

    @link()
    def stats(self, request, *args, **kwargs):
        obj = self.get_object()
        # TODO: we would need a better rating calculation in the future
        qs = obj.borrowercomments.aggregate(Avg('note'), Count('id'))
        res = {
            'average_rating': int(qs['note__avg'] or 0),
            'booking_comments_count': int(qs['id__count'] or 0),
            'bookings_count': obj.bookings.count(),
            'ratings_count': int(qs['id__count'] or 0),
        }
        return response.Response(res)

    def get_serializer(self, instance=None, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        
        We should use different Seializer classes for instances of
        Product, CarProduct and RealEstateProduct models
        """
        if hasattr(instance, 'carproduct'):
            # we have CarProduct here
            serializer_class = serializers.CarProductSerializer
            self.object = instance = instance.carproduct
        elif hasattr(instance, 'realestateproduct'):
            # we have RealEstateProduct here
            serializer_class = serializers.RealEstateProductSerializer
            self.object = instance = instance.realestateproduct
        else:
            # we have generic Product here
            serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        return serializer_class(instance, context=context, **kwargs)

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

class CuriosityViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows product curiosities to be viewed or edited.
    """
    queryset = models.Curiosity.on_site.all()
    serializer_class = serializers.CuriositySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('product',) # TODO: 'city', 'price')
    # TODO: ordering_fields = ('price',)

class MessageThreadViewSet(mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows message threads to be viewed or edited.
    """
    model = models.MessageThread
    queryset = models.MessageThread.objects.select_related('messages')
    serializer_class = serializers.MessageThreadSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend)
    owner_field = ('sender', 'recipient')
    filter_fields = ('sender', 'recipient', 'product')

class ProductRelatedMessageViewSet(mixins.SetOwnerMixin, viewsets.ModelViewSet):
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
