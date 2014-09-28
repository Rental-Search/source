# -*- coding: utf-8 -*-
import smtplib
import socket
import datetime
import urllib
import itertools

from logbook import Logger


from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

import gdata.contacts.client
import gdata.gauth


from django.views.generic import ListView
from django.views.generic.base import TemplateResponseMixin


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, BadHeaderError
from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Max, Avg
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login
from oauth_provider.models import Token
from django.shortcuts import redirect

from accounts.forms import (EmailAuthenticationForm, PatronEditForm, 
    PatronPasswordChangeForm, ContactForm, CompanyEditForm, SubscriptionEditForm,
    PatronSetPasswordForm, FacebookForm, CreditCardForm, GmailContactForm)
from accounts.models import Patron, FacebookSession, CreditCard, Billing, ProPackage, BillingHistory
from accounts.wizard import AuthenticationWizard
from accounts.choices import GEOLOCATION_SOURCE

from products.models import ProductRelatedMessage, MessageThread, Product
from products.search import product_search

from rent.models import Booking, BorrowerComment, OwnerComment
from rent.forms import OwnerCommentForm, BorrowerCommentForm
from rent.choices import BOOKING_STATE, COMMENT_TYPE_CHOICES

from eloue.geocoder import GoogleGeocoder
from eloue.decorators import secure_required, mobify, ownership_required
from eloue.views import LoginRequiredMixin
from eloue.utils import json


PAGINATE_PRODUCTS_BY = getattr(settings, 'PAGINATE_PRODUCTS_BY', 10)
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)

log = Logger('eloue.accounts')


@never_cache
@secure_required
def activate(request, activation_key):
    """Activate account"""
    activation_key = activation_key.lower()  # Normalize before trying anything with it.
    is_actived = Patron.objects.activate(activation_key)
    return render(request, 'accounts/activate.html', 
        {'is_actived': is_actived,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS} )


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
    return HttpResponse(str(csrf(request)["csrf_token"]))


@never_cache
def oauth_authorize(request, *args, **kwargs):
    return HttpResponse(str(csrf(request)["csrf_token"]))


@never_cache
def oauth_callback(request, *args, **kwargs):
    token = Token.objects.get(key=kwargs['oauth_token'])
    return HttpResponse(token.verifier)

def google_oauth_callback(request):
    return render(request, 'accounts/google_callback.html')

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
        return render(request, 'accounts/associate_facebook.html', {'form': form})
    else:
        return render(
            request, 'accounts/associated_facebook.html', 
            {'me': request.user.facebooksession.uid}
        )


@require_POST
def user_geolocation(request):
    stored_location = request.session.setdefault('location', {})

    source = int(request.POST['source'])
    if stored_location:
        current_source = stored_location.get('source', max(GEOLOCATION_SOURCE.values())+1)
        if (current_source <= source) and not json.loads(request.POST.get('forced')):
            return HttpResponse(json.dumps(
                {'status': 'already_geolocated'}),
                content_type="application/json"
            )
    
    radius = None
    
    stored_location.update({
        'source': int(request.POST['source'])
    })

    if 'address' in request.POST:
        location = json.loads(request.POST['address'])
        address_components = location['address_components']
        
        formatted_address = location.get('formatted_address')
        localities = filter(lambda component: 'locality' in component['types'], address_components)
        city = next(iter(map(lambda component: component['long_name'], localities)), None)
        regions = filter(lambda component: 'administrative_area_level_1' in component['types'], address_components)
        region = next(iter(map(lambda component: component['long_name'], regions)), None)
        countries = filter(lambda component: 'country' in component['types'], address_components)
        country = next(iter(map(lambda component: component['long_name'], countries)), None)
        fallback = next(iter(map(lambda component: component['long_name'], address_components)), None) if not (city or region or country) else None
        region_coords, region_radius = GoogleGeocoder().geocode(', '.join([region, country]))[1:3] if region and country else (None, None)

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
                    city_coords, city_radius = GoogleGeocoder().geocode(', '.join(filter(None, [city, region, country])))[1:3] if city and country else (None, None)
                    radius = city_radius or region_radius
            else:
                city_coords, city_radius = GoogleGeocoder().geocode(', '.join(filter(None, [city, region, country])))[1:3] if region and country else (None, None)
                radius = city_radius or region_radius

    if 'coordinates' in request.POST:
        coordinates = json.loads(request.POST['coordinates'])
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
    return HttpResponse(json.dumps(
        {'status': "OK", 'radius': radius}), 
        content_type="application/json"
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
        Q(state__in=[BOOKING_STATE.CLOSED, BOOKING_STATE.CLOSING, BOOKING_STATE.ENDED])
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
                    return redirect('comments')
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
    if booking.state not in (BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED, BOOKING_STATE.ENDED):
        return redirect('comments')
    
    if booking.owner == request.user:
        try:
            booking.ownercomment
        except OwnerComment.DoesNotExist:
            Form = OwnerCommentForm
            Model = OwnerComment
        else:
            return redirect('comments')
    else:
        try:
            booking.borrowercomment
        except BorrowerComment.DoesNotExist:
            Form = BorrowerCommentForm
            Model = BorrowerComment
        else:
            return redirect('comments')
    if request.POST:
        form = Form(request.POST, instance=Model(booking=booking))
        if form.is_valid():
            form.save().send_notification_comment_email()
            return redirect('comments')
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


class PatronDetail(ListView):
    paginate_by = 9
    context_object_name = 'product_list'

    def dispatch(self, *args, **kwargs):
        if 'patron_id' in kwargs:
            # This is here to be compatible with the old app
            patron = get_object_or_404(Patron.on_site, pk=kwargs['patron_id'])
            return redirect(patron, permanent=True)
        else:
            self.patron = get_object_or_404(
                Patron.on_site.select_related('default_address', 'languages'), 
                slug=kwargs.get('slug')
            )
        return super(PatronDetail, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        if self.patron.current_subscription:
            return ['accounts/company_detail.html', ]
        return ['accounts/patron_detail.html', ]
    
    def get_queryset(self):
        return product_search.filter(owner__exact=self.patron.username).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(PatronDetail, self).get_context_data(**kwargs)
        context['patron'] = self.patron
        context['borrowercomments'] = BorrowerComment.objects.filter(booking__owner=self.patron)
        context['ownercomments'] = OwnerComment.objects.filter(booking__borrower=self.patron)
        context['comments_count'] = context['borrowercomments'].count() + context['ownercomments'].count()
        context['redirect_uri'] = self.request.build_absolute_uri(reverse('patron_edit_idn_connect'))
        context['consumer_key'] = settings.IDN_CONSUMER_KEY
        context['base_url'] = settings.IDN_BASE_URL
        return context


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
    return render(request, 'accounts/patron_edit.html', {'form': form})


@login_required
def billing_object(request, year, month, day):
    from accounts.management.commands.pro_billing import minus_one_month

    date_to = datetime.date(int(year), int(month), int(day))
    billing = get_object_or_404(Billing, patron=request.user, date_to=date_to)

    date_to = billing.date_to
    date_from = billing.date_from

    subscriptions = billing.billingsubscription_set.all()
    toppositions = billing.billingproducttopposition_set.all()
    highlights = billing.billingproducthighlight_set.all()

    highlights.sum = sum(map(lambda highlight: highlight.price, highlights), 0)
    subscriptions.sum = sum(map(lambda subscription: subscription.price, subscriptions), 0)
    toppositions.sum = sum(map(lambda topposition: topposition.price, toppositions), 0)

    return render(request, 'accounts/pro_billing.html', 
        {'billing': billing, 'billing_total': billing.total_amount + billing.total_tva, 'subscriptions': subscriptions, 'toppositions': toppositions, 'highlights': highlights,
            'from': date_from, 'to': date_to, 'patron': request.user,
        })

    response = HttpResponse(str(billing), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=facture_e-loue_{year}-{month}-{day}.pdf'.format(year=year, month=month, day=day)
    return response


@login_required
def billing(request):
    patron = request.user
    billing_histories = BillingHistory.objects.filter(
            billing__patron=patron
        ).order_by('-billing__date_from', '-date')
    to = datetime.datetime.now()
    _from = datetime.datetime.combine(patron.next_billing_date(), datetime.time())
    (billing, highlights, subscriptions, toppositions, phonenotifications, 
        emailnotifications) = Billing.builder(patron, _from, to)
    
    return render(
        request, 'accounts/patron_billing.html', 
        {
            'billing': billing, 'highlights': highlights, 
            'subscriptions': subscriptions, 'toppositions': toppositions,
            'phonenotifications': phonenotifications, 'emailnotifications': emailnotifications,
            'from': _from, 'to': to, 'billing_histories': billing_histories,
        })


@login_required
def patron_edit_subscription(request, *args, **kwargs):
    patron = request.user
    current_subscription = patron.current_subscription
    now = datetime.datetime.now()
    plans = ProPackage.objects.filter(
        Q(valid_until__isnull=True, valid_from__lte=now) |
        Q(valid_until__isnull=False, valid_until__gte=now))
    if request.method == "POST":
        form = SubscriptionEditForm(request.POST)
        if form.is_valid():
            new_package = form.cleaned_data.get('subscription')
            if not current_subscription or new_package != current_subscription.propackage:
                if new_package.maximum_items is not None and new_package.maximum_items < patron.products.count():
                    messages.error(request, 'L\'abonnement choisi autorise moins d\'objets que vous avez actuellement')
                    return redirect('.')
                try:
                    patron.creditcard
                except:
                    messages.error(request, _(u'Pour un abonnement vous devez enregistrer une carte bancaire. Merci de renseigner la carte utilisée pour le paiement.'))
                    response = redirect('patron_edit_credit_card')
                    response['Location'] += '?' + urllib.urlencode({'subscription': new_package.pk})
                    return response
                else:
                    patron.subscribe(new_package)
            return redirect('.')
        else:
            messages.error(request, "WRONG ASD")
    return render(
        request, 'accounts/patron_edit_subscription.html', 
        {'plans': plans, 'current_subscription': current_subscription}
    )


@login_required
def patron_edit_password(request):
    form = PatronPasswordChangeForm(request.user, request.POST or None) \
      if request.user.has_usable_password() \
      else PatronSetPasswordForm(request.user, request.POST or None) 
    
    if form.is_valid():
        form.save()
        messages.success(request, _(u"Votre mot de passe à bien été modifié"))
    return render(request, 'accounts/patron_edit_password.html', {'form': form, 'patron': request.user})

@login_required
def patron_edit_phonenumber(request):
    from accounts.forms import PhoneNumberFormset
    if request.POST:
        formset  = PhoneNumberFormset(request.POST, instance=request.user)
        if formset.is_valid():
            formset.save()
            messages.success(request, _(u"Vos numéros de téléphones ont bien été modifiés"))
            return redirect('patron_edit_phonenumber')
    else:
        formset = PhoneNumberFormset(instance=request.user)
    return render_to_response('accounts/patron_edit_phonenumber.html', dictionary={'formset': formset}, context_instance=RequestContext(request))

@login_required
def patron_edit_credit_card(request):
    import uuid
    patron = request.user
    try:
        instance = patron.creditcard
    except CreditCard.DoesNotExist:
        instance = CreditCard(
            holder=patron, keep=True, 
            subscriber_reference=uuid.uuid4().hex
        )
    if request.method == 'POST':
        form = CreditCardForm(data=request.POST, instance=instance)
        if form.is_valid():
            subscription = request.GET.get('subscription')
            if subscription is not None:
                propackage = get_object_or_404(ProPackage, pk=subscription)
                patron.subscribe(propackage)
                messages.success(request, u'On a validé votre abonnement')
            form.save()
            messages.success(request, u'Votre carte a bien été ajouté')
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
    
    from accounts.models import Billing

    if request.user.current_subscription and any(Billing.builder(request.user, request.user.next_billing_date(), datetime.datetime.now())[1:]):
        messages.error(request, _(u"Vous avez un abonnement en cours, veuillez nous contacter à contact@e-loue.com pour supprimer votre carte."))
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
    from accounts.forms import RIBForm
    if request.method == 'POST':
        form = RIBForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _(u"Votre RIB a bien été ajouté"))
            pk = request.GET.get('accept')
            if pk:
                booking = get_object_or_404(Booking, pk=pk, state=BOOKING_STATE.AUTHORIZED, owner=request.user)
                if booking.started_at < datetime.datetime.now():
                    booking.expire()
                    booking.save()
                    messages.error(request, _(u"Votre demande est dépassée"))
                else:
                    booking.accept()
                    booking.save()
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
    from products.forms import HighlightForm
    from products.models import ProductHighlight, Product

    patron = request.user

    highlights = ProductHighlight.objects.filter(
        ended_at__isnull=True, product__owner=patron).values_list('product', flat=True)
    highlighted = patron.products.annotate(since=Max('producthighlight__started_at')).filter(id__in=highlights)
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
    from products.models import ProductTopPosition, Product
    
    def _split_products_on_topposition(products, patron):
        toppositions = ProductTopPosition.objects.filter(
            ended_at__isnull=True, product__owner=patron
        ).values_list('product', flat=True)
        in_topposition = products.annotate(since=Max('producttopposition__started_at')).filter(id__in=toppositions)
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
    in_topposition, not_in_topposition = _split_products_on_topposition(
        patron.products, patron)

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
    from accounts.forms import AddressFormSet
    if request.POST:
        formset = AddressFormSet(request.POST, instance=request.user)
        if formset.is_valid():
            formset.save()
            messages.success(request, _(u"Vos adresses ont bien été modifiées"))
            return redirect('patron_edit_addresses')
    else:
        formset = AddressFormSet(instance=request.user)
    return render_to_response('accounts/patron_edit_addresses.html', dictionary={'formset': formset}, context_instance=RequestContext(request))


@login_required
def patron_edit_opening_times(request):
    from accounts.forms import OpeningsForm, OpeningTimes
    try:
        instance = request.user.opening_times
    except OpeningTimes.DoesNotExist:
        instance = OpeningTimes(patron=request.user)
    if request.method == "POST":
        form = OpeningsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(patron_edit_opening_times)
    else:
        form = OpeningsForm(instance=instance)
    return render(request, 'accounts/patron_edit_opening_times.html', {'form': form})


@login_required
def dashboard(request):
    new_thread_ids = ProductRelatedMessage.objects.filter(
        recipient=request.user, read_at=None
    ).order_by().values('thread').distinct()
    new_threads = MessageThread.objects.filter(pk__in=[thread['thread'] for thread in new_thread_ids]).order_by('-last_message__sent_at')
    booking_demands = Booking.on_site.filter(owner=request.user, state=BOOKING_STATE.AUTHORIZED).order_by('-created_at')
    return render(request, 'accounts/dashboard.html', 
        {'thread_list': new_threads, 'booking_demands': booking_demands}, 
    )


class AddTitle(TemplateResponseMixin):
    title = None
    def get_context_data(self, **kwargs):
        context = super(AddTitle, self).get_context_data(**kwargs)
        if self.title is not None:
            context['title_page'] = self.title
        return context

class OwnerBooking(ListView, LoginRequiredMixin, AddTitle):
    template_name = 'accounts/owner_booking.html'
    paginate_by = PAGINATE_PRODUCTS_BY

class OwnerBookingAuthorized(OwnerBooking):
    def get_queryset(self):
        if self.request.user.current_subscription:
            return self.request.user.bookings.professional()
        return self.request.user.bookings.authorized().order_by('-created_at')

class OwnerBookingPending(OwnerBooking):
    title = u'Réservations à venir'
    def get_queryset(self):
        return self.request.user.bookings.pending().order_by('-created_at')

class OwnerBookingOngoing(OwnerBooking):
    title = u'Réservations en cours'
    def get_queryset(self):
        return self.request.user.bookings.ongoing().order_by('-created_at')

class OwnerBookingHistory(OwnerBooking):
    title = u'Réservations terminées'
    def get_queryset(self):
        if self.request.user.current_subscription:
            return self.request.user.bookings.professional_saw()
        return self.request.user.bookings.history().order_by('-created_at')


class OwnerProduct(ListView, LoginRequiredMixin):
    template_name = 'accounts/owner_product.html'
    paginate_by = PAGINATE_PRODUCTS_BY
    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user, is_archived=False).order_by('-created_at')

class AlertEdit(ListView, LoginRequiredMixin):
    template_name = 'accounts/alert_edit.html'
    def get_queryset(self):
        return self.request.user.alerts.all()


class BorrowerBooking(ListView, LoginRequiredMixin, AddTitle):
    template_name = 'accounts/borrower_booking.html'
    paginate_by = PAGINATE_PRODUCTS_BY

class BorrowerBookingOngoing(BorrowerBooking):
    title = u'Réservations en cours'
    def get_queryset(self):
        return self.request.user.rentals.ongoing().order_by('-created_at')

class BorrowerBookingPending(BorrowerBooking):
    title = u'Réservations à venir'
    def get_queryset(self):
        return self.request.user.rentals.pending().order_by('-created_at')

class BorrowerBookingAuthorized(BorrowerBooking):
    title = u'Demandes de réservation'
    def get_queryset(self):
        return self.request.user.rentals.authorized().order_by('-created_at')

class BorrowerBookingHistory(BorrowerBooking):
    title = u'Réservations terminées'
    def get_queryset(self):
        return self.request.user.rentals.history().order_by('-created_at')

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
    return HttpResponse(json.dumps(work_list), content_type="application/json")


@login_required
@require_GET
def accounts_studies_autocomplete(request):
    term = request.GET.get('term', '')
    schools = Patron.objects.filter(
        school__icontains=term).values('school').annotate(Count('school'))
    school_list = [{'label': school['school'], 'value': school['school']} for school in schools]
    return HttpResponse(json.dumps(school_list), content_type="application/json")

@login_required
def gmail_invite(request):
    access_token = request.GET.get('0-facebook_access_token', None)
    if access_token:
        token_info = json.load(
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
        return render(request, 'accounts/gmail_invite.html', {'initial_data': initial_data})
    else:
        return render(request, 'accounts/gmail_invite.html')

@login_required
def gmail_send_invite(request):
    if request.POST:
        form = GmailContactForm(request.POST)
        if form.is_valid():
            request.user.send_gmail_invite(form.cleaned_data['email'])
            return HttpResponse(
                json.dumps({'status': "OK"}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({'status': "KO"}),
                content_type="application/json"
            )
    else:
        return HttpResponse(
            json.dumps({'status': "KO"}),
            content_type="application/json"
        )


def patron_subscription(request):
    from accounts.wizard import ProSubscriptionWizard
    from accounts.forms import SubscriptionEditForm
    subscription_wizard = ProSubscriptionWizard([SubscriptionEditForm, EmailAuthenticationForm])
    return subscription_wizard(request)


@login_required
def facebook_invite(request):
    return render(request, 'accounts/facebook_invite.html')

@login_required
def patron_edit_notification(request):
    from accounts.models import EmailNotification, PhoneNotification
    patron = request.user
    mails = patron.emailnotification_set.filter(ended_at__isnull=True) # XXX: filter for valides only
    phones = patron.phonenotification_set.filter(ended_at__isnull=True) # XXX: filter for valides only
    if request.method == "POST":
        # need to validate them
        if 'email' in request.POST:
            from django import forms
            email_field = forms.EmailField()
            email = request.POST.get('email')
            try:
                email = email_field.clean(email)
                EmailNotification.objects.create(patron=patron, email=email)
            except forms.ValidationError:
                messages.error(request, u"Vous devez saisir une adresse email valid.")
            return redirect('.')
        elif 'phone_number' in request.POST:
            from django.contrib.localflavor.fr import forms
            phone_field = forms.FRPhoneNumberField()
            phone_number = request.POST.get('phone_number')
            try:
                phone_number = phone_field.clean(phone_number)
                PhoneNotification.objects.create(patron=patron, phone_number=phone_number)
            except forms.ValidationError:
                messages.error(request, u"Vous devez saisir une numéro de téléphone valide")
            return redirect('.')
        elif 'email_delete' in request.POST:
            emailnotification = get_object_or_404(EmailNotification, pk=request.POST.get('email_delete'))
            emailnotification.ended_at = datetime.datetime.now()
            emailnotification.save()
            return redirect('.')
        elif 'phonenumber_delete' in request.POST:
            phonenotification = get_object_or_404(PhoneNotification, pk=request.POST.get('phonenumber_delete'))
            phonenotification.ended_at = datetime.datetime.now()
            phonenotification.save()
            return redirect('.')
        else:
            return HttpResponseForbidden()
    return render(
        request, 'accounts/patron_edit_notification.html', 
        {'mails': mails, 'phones': phones}
    )

@login_required
def patron_edit_idn_connect(request):
    import oauth2 as oauth
    import urllib, urlparse
    import urllib, json
    from accounts.models import IDNSession
    scope = '["namePerson/friendly","namePerson","contact/postalAddress/home","contact/email","namePerson/last","namePerson/first"]'

    consumer_key = settings.IDN_CONSUMER_KEY
    consumer_secret = settings.IDN_CONSUMER_SECRET
    base_url = settings.IDN_BASE_URL
    
    request_token_url = base_url + 'oauth/requestToken'
    authorize_url = base_url + 'oauth/authorize'
    access_token_url = base_url + 'oauth/accessToken'
    me_url = base_url + 'anywhere/me?oauth_scope=%s' % (scope, )
    redirect_uri = request.build_absolute_uri(reverse('patron_edit_idn_connect'))
    
    try:
        request.user.idnsession
    except IDNSession.DoesNotExist:
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        client = oauth.Client(consumer)

        if request.GET.get('connected'):

            response, content = client.request(request_token_url, "GET")
            request_token = dict(urlparse.parse_qsl(content))
            request.session['request_token'] = request_token
            link = "%s?oauth_token=%s&oauth_callback=%s&oauth_scope=%s" % (
                authorize_url, 
                request_token['oauth_token'], 
                redirect_uri, 
                scope
            )
            return redirect(link)
        elif request.GET.get('oauth_verifier'):
            idn_oauth_verifier = request.GET.get('oauth_verifier')
            request_token = oauth.Token(
                request.session['request_token']['oauth_token'],
                request.session['request_token']['oauth_token_secret'])
            request_token.set_verifier(idn_oauth_verifier)
            client = oauth.Client(consumer, request_token)
            response, content = client.request(access_token_url, "GET")
            assert json.loads(response['status']) == 200
            access_token_data = dict(urlparse.parse_qsl(content))
            access_token = oauth.Token(access_token_data['oauth_token'],
                access_token_data['oauth_token_secret'])
            client = oauth.Client(consumer, access_token)
            response, content = client.request(me_url, "GET")
            assert json.loads(response['status']) == 200
            content = json.loads(content)
            IDNSession.objects.create(
                user=request.user,
                access_token=access_token_data['oauth_token'],
                access_token_secret=access_token_data['oauth_token_secret'],
                uid=content['id'],
            )
    return render(request, 'accounts/patron_edit_idn.html', {'redirect_uri': redirect_uri, 'consumer_key': consumer_key, 'base_url': base_url})

@login_required
def patron_delete_idn_connect(request):
    from accounts.models import IDNSession
    idn = get_object_or_404(IDNSession, user=request.user)
    try:
        idn.delete()
    except:
        pass
    return redirect('patron_edit_idn_connect')



# REST API 2.0

from rest_framework import status
from rest_framework.decorators import link, action
from rest_framework.response import Response

from accounts import serializers, models, search
from accounts.utils import viva_check_phone
from eloue.api import viewsets, filters, mixins, permissions

USER_ME = 'me'

class UserViewSet(mixins.OwnerListPublicSearchMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Patron.objects.select_related('default_address', 'default_number')
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.UserPermissions,)
    filter_backends = (filters.HaystackSearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'id'
    search_index = search.patron_search
    filter_fields = ('is_professional', 'is_active')
    ordering_fields = ('username', 'first_name', 'last_name')

    def dispatch(self, request, *args, **kwargs):
        pk_field = getattr(self, 'pk_url_kwarg', 'pk')
        if kwargs.get(pk_field, None) == USER_ME and not request.user.is_anonymous():
            kwargs[pk_field] = request.user.pk
        return super(UserViewSet, self).dispatch(request, *args, **kwargs)

    @action(methods=['post', 'put'])
    def reset_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = serializers.PasswordChangeSerializer(instance=user, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': _(u"Votre mot de passe à bien été modifié")})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @link()
    def stats(self, request, *args, **kwargs):
        obj = self.get_object()
        res = {
            k: getattr(obj, k) for k in ('response_rate', 'response_time')
        }
        qs = obj.products.select_related('bookings__comments') \
            .filter(bookings__comments__type=COMMENT_TYPE_CHOICES.BORROWER) \
            .aggregate(Avg('bookings__comments__note'), Count('bookings__comments__id'))
        res.update({
            # TODO: we would need a better rating calculation in the future
            'average_rating': int(qs['bookings__comments__note__avg'] or 0),
            'ratings_count': int(qs['bookings__comments__id__count'] or 0),
            # count message threads where we have unread messages forthe requested user
            'unread_message_threads_count': obj.received_messages \
                .filter(read_at=None) \
                .values('productrelatedmessage__thread') \
                .annotate(Count('productrelatedmessage__thread')) \
                .order_by().count(),
            # count incoming booking requests for the requested user
            'booking_requests_count': obj.bookings.filter(state=BOOKING_STATE.AUTHORIZED).only('id').count(),
            'bookings_count': obj.bookings.count(),
            'products_count': obj.products.count(),
        })
        return Response(res)

class AddressViewSet(mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows addresses to be viewed or edited.
    """
    model = models.Address
    serializer_class = serializers.AddressSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter) 
    filter_fields = ('patron', 'zipcode', 'city', 'country')
    ordering_fields = ('city', 'country')

class PhoneNumberViewSet(mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows phone numbers to be viewed or edited.
    Phone numbers are sent to the borrower and to the owner for each booking.
    """
    model = models.PhoneNumber
    serializer_class = serializers.PhoneNumberSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend) 
    filter_fields = ('patron',)

    @link()
    def premium_rate_number(self, request, *args, **kwargs):
        # get current object
        obj = self.get_object()

        # get call details by number and request parameters (e.g. REMOTE_ADDR)
        tags = viva_check_phone(obj.number, request=request)

        # check for errors
        error = int(tags.get('error', 0))
        if error:
            return Response(
                {'error': error, 'error_msg': tags.get('error_msg', '')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(tags)

class CreditCardViewSet(mixins.SetOwnerMixin, viewsets.NonEditableModelViewSet):
    """
    API endpoint that allows credit cards to be viewed or edited.
    Credit card is used to pay the booking. During the booking request pre-approval payment is done.
    After if the owner accept the booking we make the payment.
    """
    model = models.CreditCard
    serializer_class = serializers.CreditCardSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend)
    owner_field = 'holder'
    filter_fields = ('holder',)

class ProAgencyViewSet(mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows professional agencies to be viewed or edited.
    ProAgency lists all agencies of a pro renter.
    """
    model = models.ProAgency
    serializer_class = serializers.ProAgencySerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('patron', 'zipcode', 'city', 'country')
    ordering_fields = ('city', 'country')

class ProPackageViewSet(viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows professional packages to be viewed or edited.
    ProPackage is subscribed by pro renter to access to e-loue and publish their goods online.
    """
    model = models.ProPackage
    permission_classes = (permissions.IsStaffOrReadOnly,)
    serializer_class = serializers.ProPackageSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('maximum_items', 'price', 'valid_from', 'valid_until')
    ordering_fields = ('name', 'maximum_items', 'price', 'valid_from', 'valid_until')

class SubscriptionViewSet(mixins.SetOwnerMixin, viewsets.NonDeletableModelViewSet):
    """
    API endpoint that allows subscriptions to be viewed or edited.
    Subcriptions are the means through what pro renters subscribe for ProPackages.
    """
    model = models.Subscription
    serializer_class = serializers.SubscriptionSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('patron', 'propackage', 'subscription_started', 'subscription_ended', 'payment_type')
    ordering_fields = ('subscription_started', 'subscription_ended', 'payment_type')

class BillingViewSet(mixins.SetOwnerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows billings to be viewed or edited.
    """
    model = models.Billing
    serializer_class = serializers.BillingSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('patron',)
    ordering_fields = ('created_at',)

class BillingSubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows sbilling ubscriptions to be viewed or edited.
    """
    model = models.BillingSubscription
    serializer_class = serializers.BillingSubscriptionSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = 'billing__patron'
    filter_fields = ('subscription', 'billing', 'price')
    ordering_fields = ('price',)
