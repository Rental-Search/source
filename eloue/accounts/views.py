# -*- coding: utf-8 -*-
import smtplib
import socket
import datetime, time
import urllib
import simplejson
import itertools

from logbook import Logger
import simplejson


from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

import gdata.contacts.client
import gdata.gauth

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, BadHeaderError, send_mass_mail
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.views.decorators.http import require_GET
from django.forms.models import model_to_dict, inlineformset_factory
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login
from oauth_provider.models import Token
from django.shortcuts import redirect
 
from eloue.decorators import secure_required, mobify, ownership_required
from eloue.accounts.forms import (EmailAuthenticationForm, GmailContactFormset, PatronEditForm, 
    PatronPasswordChangeForm, ContactForm, CompanyEditForm,
    PatronSetPasswordForm, FacebookForm, CreditCardForm, GmailContactForm)
from eloue.accounts.models import Patron, FacebookSession, CreditCard, Billing

from eloue.accounts.wizard import AuthenticationWizard

from eloue import geocoder
from eloue.products.forms import FacetedSearchForm

from eloue.products.models import ProductRelatedMessage, MessageThread
from eloue.products.search_indexes import product_search
from eloue.rent.models import Booking, BorrowerComment, OwnerComment
from eloue.rent.forms import OwnerCommentForm, BorrowerCommentForm
import time


PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

log = Logger('eloue.accounts')


@never_cache
@secure_required
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower()  # Normalize before trying anything with it.
    is_actived = Patron.objects.activate(activation_key)
    return direct_to_template(request, 'accounts/activate.html', extra_context={'is_actived': is_actived,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS})


@never_cache
@secure_required
def authenticate(request, *args, **kwargs):
    if request.user.is_anonymous():
        wizard = AuthenticationWizard([EmailAuthenticationForm])
        return wizard(request, *args, **kwargs)
    else:
        redirect_path = request.GET.get('next', '')
        if redirect_path:
            return redirect(redirect_path)
        else:
            return redirect(settings.LOGIN_REDIRECT_URL)

@never_cache
def authenticate_headless(request):
    form = EmailAuthenticationForm(request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return HttpResponse()
    return HttpResponse(csrf(request)["csrf_token"]._proxy____func())


@never_cache
def oauth_authorize(request, *args, **kwargs):
    return HttpResponse(csrf(request)["csrf_token"]._proxy____func())


@never_cache
def oauth_callback(request, *args, **kwargs):
    token = Token.objects.get(key=kwargs['oauth_token'])
    return HttpResponse(token.verifier)

def google_oauth_callback(request):
    return direct_to_template(request, 'accounts/google_callback.html')

@never_cache
@login_required
def associate_facebook(request):
    try:
        request.user.facebooksession
    except FacebookSession.DoesNotExist:
        form = FacebookForm(request.POST or None)
        form.user = request.user
        if form.is_valid():
            return redirect('associate_facebook')
        return direct_to_template(request, 'accounts/associate_facebook.html', {'form': form})
    else:
        return direct_to_template(
            request, 'accounts/associated_facebook.html', 
            {'me': request.user.facebooksession.uid}
        )


from eloue.products.utils import Enum

GEOLOCATION_SOURCE = Enum([
    (1, 'MANUAL', _('Location set manually')),
    (2, 'BROWSER', _('Location set by browser geocoding')),
    (3, 'ADDRESS', _('Location set by user address')),
    (4, 'DEFAULT', _('Default location'))
])

@require_POST
def user_geolocation(request):
    stored_location = request.session.setdefault('location', {})

    source = int(request.POST['source'])
    if stored_location:
        current_source = stored_location.get('source', max(GEOLOCATION_SOURCE.values())+1)
        if (current_source <= source) and not simplejson.loads(request.POST.get('forced')):
            return HttpResponse(simplejson.dumps(
                {'status': 'already_geolocated'}),
                mimetype="application/json"
            )
    
    radius = None
    
    stored_location.update({
        'source': int(request.POST['source'])
    })

    if 'address' in request.POST:
        location = simplejson.loads(request.POST['address'])
        address_components = location['address_components']
        
        formatted_address = location.get('formatted_address')
        localities = filter(lambda component: 'locality' in component['types'], address_components)
        city = next(iter(map(lambda component: component['long_name'], localities)), None)
        regions = filter(lambda component: 'administrative_area_level_1' in component['types'], address_components)
        region = next(iter(map(lambda component: component['long_name'], regions)), None)
        countries = filter(lambda component: 'country' in component['types'], address_components)
        country = next(iter(map(lambda component: component['long_name'], countries)), None)
        fallback = next(iter(map(lambda component: component['long_name'], address_components)), None) if not (city or region or country) else None
        region_coords, region_radius = geocoder.GoogleGeocoder().geocode(', '.join([region, country]))[1:3] if region and country else (None, None)

        stored_location.update({
            'city': city,
            'region': region,
            'region_radius': region_radius,
            'region_coords': region_coords,
            'country': country,
            'fallback': fallback,
            'formatted_address': formatted_address,
        })
        if 'radius' not in request.POST:
            if source == GEOLOCATION_SOURCE.MANUAL:
                try:
                    viewport = location['geometry']['viewport']
                    latitudes = viewport.get('Y') or viewport['ba']
                    longitudes = viewport['$']
                    from geopy import distance, Point
                    sw = Point(latitudes['b'], longitudes['b'])
                    ne = Point(latitudes['d'], longitudes['d'])
                    radius = (distance.distance(sw, ne).km // 2) + 1
                except KeyError as e:
                    city_coords, city_radius = geocoder.GoogleGeocoder().geocode(', '.join(filter(None, [city, region, country])))[1:3] if city and country else (None, None)
                    radius = city_radius or region_radius
            else:
                city_coords, city_radius = geocoder.GoogleGeocoder().geocode(', '.join(filter(None, [city, region, country])))[1:3] if region and country else (None, None)
                radius = city_radius or region_radius

    if 'coordinates' in request.POST:
        coordinates = simplejson.loads(request.POST['coordinates'])
        coordinates = (coordinates['lat'], coordinates['lon'])
        stored_location.update({
            'coordinates': coordinates
        })
    
    if 'radius' in request.POST:
        radius = int(float(request.POST['radius']))

    stored_location.update({
        'radius': radius
    })

    request.session.save()
    return HttpResponse(simplejson.dumps(
        {'status': "OK", 'radius': radius}), 
        mimetype="application/json"
    )

@require_GET
def get_user_location(request):
    location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
    location_text = location.get('formatted_address') or location['city'] or location['region'] or location['country'] or location['fallback']
    return HttpResponse(location_text)

@login_required
def comments_received(request):
    patron = request.user
    borrowers_comments = BorrowerComment.objects.filter(booking__owner=patron)
    owners_comments = OwnerComment.objects.filter(booking__borrower=patron)
    return render_to_response(
        'rent/comments_received.html',
        RequestContext(request, {
            'borrowers_comments': borrowers_comments,
            'owners_comments': owners_comments,
        })
    )


@login_required
def comments(request):
    patron = request.user
    closed_bookings = Booking.objects.filter(
        Q(owner=patron) | Q(borrower=patron), 
        Q(state=Booking.STATE.CLOSED)|Q(state=Booking.STATE.CLOSING)|Q(state=Booking.STATE.ENDED)
    )
    commented_bookings = closed_bookings.filter(
        ~Q(ownercomment=None, owner=patron) & 
        ~Q(borrower=patron, borrowercomment=None)
    )
    uncommented_bookings = closed_bookings.filter(
        Q(ownercomment=None, owner=patron) | 
        Q(borrower=patron, borrowercomment=None)
    )
    forms = []

    if request.method == "POST":
        for booking in uncommented_bookings:
            if booking.owner == patron:
                Form = OwnerCommentForm
                Model = OwnerComment
            else:
                Form = BorrowerCommentForm
                Model = BorrowerComment
            
            if unicode(booking.pk.hex) in request.POST:
                form = Form(request.POST, instance=Model(booking=booking), prefix=booking.pk)
                if form.is_valid():
                    form.save().send_notification_comment_email()
                    return redirect('eloue.accounts.views.comments')
            else:
                form = Form(instance=Model(booking=booking), prefix=booking.pk)
            forms.append(form)
    else:
        for booking in uncommented_bookings:
            if booking.owner == patron:
                Form = OwnerCommentForm
                Model = OwnerComment
            else:
                Form = BorrowerCommentForm
                Model = BorrowerComment
            form = Form(instance=Model(booking=booking), prefix=booking.pk)
            forms.append(form)
    
    return render_to_response(
        'rent/comments.html', 
        RequestContext(
            request, 
            {
                'commented_bookings': commented_bookings,
                'forms': forms,
            }
        )
    )

@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def comment_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    if booking.state not in (Booking.STATE.CLOSING, Booking.STATE.CLOSED, Booking.STATE.ENDED):
        return redirect('eloue.accounts.views.comments')
    
    if booking.owner == request.user:
        try:
            booking.ownercomment
        except OwnerComment.DoesNotExist:
            Form = OwnerCommentForm
            Model = OwnerComment
        else:
            return redirect('eloue.accounts.views.comments')
    else:
        try:
            booking.borrowercomment
        except BorrowerComment.DoesNotExist:
            Form = BorrowerCommentForm
            Model = BorrowerComment
        else:
            return redirect('eloue.accounts.views.comments')
    if request.POST:
        form = Form(request.POST, instance=Model(booking=booking))
        if form.is_valid():
            form.save().send_notification_comment_email()
            return redirect('eloue.accounts.views.comments')
    else:
        form = Form(instance=Model(booking=booking))
    return render_to_response(
        template_name='rent/comment.html',
        context_instance=RequestContext(
            request, {'form': form}
        )
    )

@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def view_comment(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    return render_to_response(
        template_name='rent/comment_view.html',
        context_instance=RequestContext(request, {'booking': booking})
    )

@cache_page(900)
def patron_detail(request, slug, patron_id=None, page=None):
    if patron_id:  # This is here to be compatible with the old app
        patron = get_object_or_404(Patron.on_site, pk=patron_id)
        return redirect_to(request, patron.get_absolute_url(), permanent=True)
    patron = get_object_or_404(Patron.on_site.select_related('default_address', 'languages'), slug=slug)
    patron_products = product_search.filter(owner_exact=patron.username)
    if patron.is_professional:
        template_name = 'accounts/company_detail.html'
    else:
        template_name = 'accounts/patron_detail.html'

    return object_list(
        request, patron_products, page=page, 
        paginate_by=9, template_name=template_name, 
        template_object_name='product', 
        extra_context={
            'patron': patron, 'product_list_count': patron_products.count(), 
            'borrowercomments': BorrowerComment.objects.filter(booking__owner=patron)[:4]
        }
    )


@login_required
def patron_edit(request, *args, **kwargs):
    if request.user.is_professional:
        form = CompanyEditForm(request.POST or None, request.FILES or None, instance=request.user)
    else:
        form = PatronEditForm(request.POST or None, request.FILES or None, instance=request.user)

    if form.is_valid():
        form.save()
        messages.success(request, _(u"Vos informations ont bien été modifiées")) 
        return redirect(reverse('patron_edit'))
    
    return direct_to_template(
        request, 'accounts/patron_edit.html', 
        extra_context={
            'form': form
        }
    )


@login_required
def billing_object(request, year, month, day):
    billing = get_object_or_404(
        Billing, patron=request.user, 
        date=datetime.date(int(year), int(month), int(day)))
    response = HttpResponse(str(billing), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=facture_e-loue_{year}-{month}-{day}.pdf'.format(year=year, month=month, day=day)
    return response


@login_required
def billing(request):
    import calendar

    patron = request.user
    billings = patron.billing_set.order_by('date')

    to = datetime.datetime.now()
    if billings:
        date = datetime.datetime.combine(billings[-1].date, datetime.time())
        days = calendar.monthrange(date.year, date.month)
        _from = date + datetime.timedelta(days=days)
    else:
        s = patron.subscription_set.order_by('subscription_started')
        if s:
            _from  = datetime.datetime.combine(
                patron.subscription_set.order_by(
                    'subscription_started'
                )[0].subscription_started.date(), datetime.time())
        else:
            _from = to

    billing, highlights, subscriptions = Billing.builder(patron, _from, to)
    highlights_sum = sum(map(lambda highlight: highlight.price(_from, to), highlights), 0)
    subscriptions_sum = sum(map(lambda subscription: subscription.price(_from, to), subscriptions), 0)
    return render(
        request, 'accounts/patron_billing.html', 
        {
            'billings': billings, 'billing': billing, 
            'highlights': highlights, 'subscriptions': subscriptions,
            'highlights_sum': highlights_sum, 'subscriptions_sum': subscriptions_sum,
            'from': _from, 'to': to, 'sum': highlights_sum + subscriptions_sum
        })


@login_required
def patron_edit_subscription(request, *args, **kwargs):
    from eloue.accounts.forms import SubscriptionEditForm
    from eloue.accounts.models import Subscription, ProPackage
    patron = request.user
    if not patron.is_professional:
        return HttpResponseForbidden()
    subscription, = Subscription.objects.filter(patron=patron, subscription_ended__isnull=True) or (None,)
    now = datetime.datetime.now()
    plans = ProPackage.objects.filter(
        Q(valid_until__isnull=True, valid_from__lte=now) or
        Q(valid_until__isnull=False, valid_until__gte=now))
    if request.method == "POST":
        form = SubscriptionEditForm(request.POST)
        if form.is_valid():
            new_package = form.cleaned_data.get('subscription')
            if (subscription is None and new_package) or (new_package != subscription.propackage):
                if subscription:
                    subscription.subscription_ended = datetime.datetime.now()
                    subscription.save()
                if new_package:
                    Subscription.objects.create(patron=patron, propackage=new_package)
            return redirect('.')
        else:
            messages.error(request, "WRONG ASD")
    return render(
        request, 'accounts/patron_edit_subscription.html', 
        {'plans': plans, 'current_subscription': subscription}
    )


@login_required
def patron_edit_password(request):
    
    form = PatronPasswordChangeForm(request.user, request.POST or None) \
      if request.user.has_usable_password() \
      else PatronSetPasswordForm(request.user, request.POST or None) 
    
    if form.is_valid():
        form.save()
        messages.success(request, _(u"Votre mot de passe à bien été modifié"))
    return direct_to_template(request, 'accounts/patron_edit_password.html', extra_context={'form': form, 'patron': request.user})

@login_required
def patron_edit_phonenumber(request):
    from eloue.accounts.forms import PhoneNumberFormset
    if request.POST:
        formset  = PhoneNumberFormset(request.POST, instance=request.user)
        if formset.is_valid():
            formset.save()
            messages.success(request, _(u"Vos numéros de téléphones ont bien été modifiés"))
            return redirect('eloue.accounts.views.patron_edit_phonenumber')
    else:
        formset = PhoneNumberFormset(instance=request.user)
    return render_to_response('accounts/patron_edit_phonenumber.html', dictionary={'formset': formset}, context_instance=RequestContext(request))

@login_required
def patron_edit_credit_card(request):
    import uuid
    try:
        instance = request.user.creditcard
    except CreditCard.DoesNotExist:
        instance = CreditCard(
            holder=request.user, keep=True, 
            subscriber_reference=uuid.uuid4().hex
        )
    if request.method == 'POST':
        form = CreditCardForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(patron_edit_credit_card)
    else:
        form = CreditCardForm(data=None, instance=instance)
    return render_to_response(
        template_name='accounts/patron_edit_credit_card.html', 
        dictionary={'form': form}, context_instance=RequestContext(request))

@login_required
def patron_delete_credit_card(request):
    try:
        instance = request.user.creditcard
        if not instance.keep:
            messages.error(request, _(u"Vous n'avez pas de carte enregistrée"))
            return redirect(patron_edit_credit_card)
    except CreditCard.DoesNotExist:
        messages.error(request, _(u"Vous n'avez pas de carte enregistrée"))
        return redirect(patron_edit_credit_card)
    
    if instance.payboxdirectpluspaymentinformation_set.all():
        instance.holder = None
        instance.save()
    else:
        instance.delete()

    messages.success(request, _(u"On a bien supprimé les détails de votre carte bancaire."))
    return redirect(patron_edit_credit_card)


@login_required
def patron_edit_rib(request):
    from eloue.accounts.forms import RIBForm
    if request.method == 'POST':
        form = RIBForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _(u"Votre RIB a bien été ajouté"))
            pk = request.GET.get('accept')
            if pk:
                booking = get_object_or_404(Booking, pk=pk, state=Booking.STATE.AUTHORIZED, owner=request.user)
                if booking.started_at < datetime.datetime.now():
                    booking.state = booking.STATE.OUTDATED
                    booking.save()
                    messages.error(request, _(u"Votre demande est dépassée"))
                else:
                    booking.accept()
                    messages.success(request, _(u"La demande de location a été acceptée"))
                    GoalRecord.record('rent_object_accepted', WebUser(request))
                return redirect(booking)
            else:
                return redirect(patron_edit_rib)
    else:
        form = RIBForm(data=None, instance=request.user)
    return render_to_response(
        template_name='accounts/patron_edit_rib.html',
        dictionary={'form': form}, context_instance=RequestContext(request)
    )


@login_required
def patron_edit_highlight(request):
    from eloue.products.forms import HighlightForm
    from eloue.products.models import ProductHighlight, Product

    patron = request.user

    highlights = ProductHighlight.objects.filter(
        ended_at__isnull=True).values_list('product', flat=True)
    highlighted = patron.products.filter(id__in=highlights)
    not_highlighted = patron.products.filter(~Q(id__in=highlights))
    if request.method == "POST":
        try:
            product_id = int(request.POST.get('product'))
        except ValueError:
            return HttpResponseForbidden()
        product = get_object_or_404(patron.products, pk=product_id)
        now = datetime.datetime.now()
        highlights = product.producthighlight_set.order_by('-ended_at')
        old_highlights = product.producthighlight_set.filter(ended_at__isnull=False).order_by('-ended_at')
        new_highlight = product.producthighlight_set.filter(ended_at__isnull=True)
        if new_highlight:
            highlight, = new_highlight
            highlight.ended_at = now
            highlight.save()
        else:
            ProductHighlight.objects.create(product=product)
        return redirect('.')

    return render_to_response(
        template_name='accounts/patron_edit_highlight.html',
        dictionary={
            'highlighted': highlighted,
            'not_highlighted': not_highlighted,
        }, 
        context_instance=RequestContext(request)
    )


@login_required
def patron_edit_top_position(request):
    from eloue.products.models import ProductTopPosition, Product
    
    def _split_products_on_topposition(products):
        toppositions = ProductTopPosition.objects.filter(ended_at__isnull=True).values_list('product', flat=True)
        in_topposition = products.filter(id__in=toppositions)
        not_in_topposition = products.filter(~Q(id__in=toppositions))
        return in_topposition, not_in_topposition

    def _toggle_topposition(product):
        now = datetime.datetime.now()
        highlights = product.producttopposition_set.order_by('-ended_at')
        old_highlights = product.producttopposition_set.filter(ended_at__isnull=False).order_by('-ended_at')
        new_highlight = product.producttopposition_set.filter(ended_at__isnull=True)
        if new_highlight:
            highlight, = new_highlight
            highlight.ended_at = now
            highlight.save()
        else:
            ProductTopPosition.objects.create(product=product)

    patron = request.user
    in_topposition, not_in_topposition = _split_products_on_topposition(patron.products)

    if request.method == "POST":
        try:
            product_id = int(request.POST.get('product'))
        except ValueError:
            return HttpResponseForbidden()
        product = get_object_or_404(patron.products, pk=product_id)
        _toggle_topposition(product)
        return redirect('.')

    return render_to_response(
        template_name='accounts/patron_edit_top_position.html',
        dictionary={
            'in_topposition': in_topposition,
            'not_in_topposition': not_in_topposition,
        }, 
        context_instance=RequestContext(request)
    )

@login_required
def patron_edit_addresses(request):
    from eloue.accounts.forms import AddressFormSet
    if request.POST:
        formset = AddressFormSet(request.POST, instance=request.user)
        if formset.is_valid():
            formset.save()
            messages.success(request, _(u"Vos adresses ont bien été modifiées"))
            return redirect('eloue.accounts.views.patron_edit_addresses')
    else:
        formset = AddressFormSet(instance=request.user)
    return render_to_response('accounts/patron_edit_addresses.html', dictionary={'formset': formset}, context_instance=RequestContext(request))


@login_required
def patron_edit_opening_times(request):
    from eloue.accounts.forms import OpeningsForm, OpeningTimes
    try:
        instance = request.user.openingtimes
    except OpeningTimes.DoesNotExist:
        instance = OpeningTimes(patron=request.user)
    if request.method == "POST":
        form = OpeningsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(patron_edit_opening_times)
    else:
        form = OpeningsForm(instance=instance)
    return render_to_response('accounts/patron_edit_opening_times.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def dashboard(request):
    new_thread_ids = ProductRelatedMessage.objects.filter(
        recipient=request.user, read_at=None
    ).order_by().values('thread').distinct()
    new_threads = MessageThread.objects.filter(pk__in=[thread['thread'] for thread in new_thread_ids]).order_by('-last_message__sent_at')
    booking_demands = Booking.on_site.filter(owner=request.user, state=Booking.STATE.AUTHORIZED).order_by('-created_at')
    return render_to_response(
        template_name='accounts/dashboard.html', 
        dictionary={'thread_list': new_threads, 'booking_demands': booking_demands}, 
        context_instance=RequestContext(request)
    )
    return direct_to_template(
        request, 'accounts/dashboard.html', {}
    )


@login_required
def owner_booking_authorized(request, page=None):
    queryset = request.user.bookings.professional() if request.user.is_professional else request.user.bookings.authorized()
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Demandes de réservation'},
        template_name='accounts/owner_booking.html'
    )

@login_required
def owner_booking_pending(request, page=None):
    queryset = request.user.bookings.pending()
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations à venir'},
        template_name='accounts/owner_booking.html'
    )

@login_required
def owner_booking_ongoing(request, page=None):
    queryset = request.user.bookings.ongoing()
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations en cours'},
        template_name='accounts/owner_booking.html'
    )

@login_required
def owner_booking_history(request, page=None):
    queryset = request.user.bookings.history()
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations terminées'},
        template_name='accounts/owner_booking.html')

# @login_required
# def owner_history(request, page=None):
#     queryset = request.user.bookings.filter(state__in=[Booking.STATE.CLOSED, Booking.STATE.REJECTED])
#     return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/owner_history.html',
#         template_object_name='booking')


@login_required
def owner_product(request, page=None):
    queryset = request.user.products.all()
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/owner_product.html',
        template_object_name='product')

@login_required
def alert_edit(request, page=None):
    queryset = request.user.alerts.all()
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/alert_edit.html',
        template_object_name='alert')

@login_required
def borrower_booking_ongoing(request, page=None):
    queryset = request.user.rentals.ongoing()
    return object_list(
        request, queryset, page=page, paginate_by=10,
        extra_context={'title_page': u'Réservations en cours'},
        template_name='accounts/borrower_booking.html')

@login_required
def borrower_booking_pending(request, page=None):
    queryset = request.user.rentals.pending()
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations à venir'},
        template_name='accounts/borrower_booking.html')

@login_required
def borrower_booking_authorized(request, page=None):
    queryset = request.user.rentals.authorized()
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Demandes de réservation'},
        template_name='accounts/borrower_booking.html')

@login_required
def borrower_booking_history(request, page=None):
    queryset = request.user.rentals.exclude(
        state__in=[
            Booking.STATE.ONGOING, 
            Booking.STATE.PENDING, 
            Booking.STATE.AUTHORIZED,
            Booking.STATE.AUTHORIZING,
            Booking.STATE.OUTDATED
        ]
    )
    return object_list(
        request, queryset, page=page, paginate_by=10,
        extra_context={'title_page': u'Réservations terminées'},
        template_name='accounts/borrower_booking.html'
    )

@mobify
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            headers = {'Reply-To': form.cleaned_data['sender']}
            if form.cleaned_data.get('cc_myself'):
                headers['Cc'] = form.cleaned_data['sender']
            
            domain = ".".join(Site.objects.get_current().domain.split('.')[1:])
            email = EmailMessage(form.cleaned_data['subject'], form.cleaned_data['message'],
                settings.DEFAULT_FROM_EMAIL, ['contact@%s' % domain], headers=headers)
            try:
                email.send()
                messages.success(request, _(u"Votre message a bien été envoyé"))
                return redirect(contact)
            except (BadHeaderError, smtplib.SMTPException, socket.error):
                messages.error(request, _(u"Erreur lors de l'envoi du message"))
    else:
        form = ContactForm()
    return render_to_response(
        template_name='accounts/contact.html', dictionary={'form': form}, 
        context_instance=RequestContext(request)
    )

@login_required
@require_GET
def accounts_work_autocomplete(request):
    term = request.GET.get('term', '')
    works = Patron.objects.filter(
        work__icontains=term).values('work').annotate(Count('work'))
    work_list = [{'label': work['work'], 'value': work['work']} for work in works]
    return HttpResponse(simplejson.dumps(work_list), mimetype="application/json")


@login_required
@require_GET
def accounts_studies_autocomplete(request):
    term = request.GET.get('term', '')
    schools = Patron.objects.filter(
        school__icontains=term).values('school').annotate(Count('school'))
    school_list = [{'label': school['school'], 'value': school['school']} for school in schools]
    return HttpResponse(simplejson.dumps(school_list), mimetype="application/json")

@login_required
def gmail_invite(request):
    access_token = request.GET.get('0-facebook_access_token', None)
    if access_token:
        token_info = simplejson.load(
            urllib.urlopen(
                'https://www.googleapis.com/oauth2/v1/'
                'tokeninfo?access_token=%s'%access_token
            )
        )
        if 'audience' not in token_info or token_info['audience'] != settings.GOOGLE_CLIENT_ID:
            return HttpResponseForbidden()
        client = gdata.contacts.client.ContactsClient(source='e-loue')
        token = gdata.gauth.OAuth2Token(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scope=('https://www.googleapis.com/auth/userinfo.email+'
                'https://www.googleapis.com/auth/userinfo.profile+'
                'https://www.google.com/m8/feeds'
            ), user_agent='', access_token=access_token
        )
        client = token.authorize(client)
        query = gdata.contacts.client.ContactsQuery()
        query.max_results = 10000
        initial_data = []
        for e in client.GetContacts(q=query).entry:
            email = next(itertools.imap(lambda email: email.address, itertools.ifilter(lambda email: email.primary and email.primary=='true', e.email)), None)
            if email:
                initial_data.append({'checked': False, 'name': e.name.full_name.text if e.name else '', 'email': email})
        return direct_to_template(request, 'accounts/gmail_invite.html', {'initial_data': initial_data})
    else:
        return direct_to_template(request, 'accounts/gmail_invite.html')

@login_required
def gmail_send_invite(request):
    if request.POST:
        form = GmailContactForm(request.POST)
        if form.is_valid():
            request.user.send_gmail_invite(form.cleaned_data['email'])
            return HttpResponse(
                simplejson.dumps({'status': "OK"}), 
                mimetype="application/json"
            )
        else:
            return HttpResponse(
                simplejson.dumps({'status': "KO"}), 
                mimetype="application/json"
            )
    else:
        return HttpResponse(
            simplejson.dumps({'status': "KO"}), 
            mimetype="application/json"
        )




@login_required
def facebook_invite(request):
    return direct_to_template(request, 'accounts/facebook_invite.html')

@login_required
def patron_edit_notification(request):
    return direct_to_template(request, 'accounts/patron_edit_notification.html')
