# -*- coding: utf-8 -*-
import smtplib
import socket
import simplejson
from logbook import Logger
import simplejson

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, BadHeaderError
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.views.decorators.http import require_GET
from django.forms.models import model_to_dict, inlineformset_factory
from django.shortcuts import get_object_or_404, render_to_response
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
from eloue.accounts.forms import EmailAuthenticationForm, PatronEditForm, MoreInformationForm, PatronPaypalForm, PatronPasswordChangeForm, ContactForm, PatronSetPasswordForm, FacebookForm
from eloue.accounts.models import Patron, FacebookSession
from eloue.accounts.wizard import AuthenticationWizard

from eloue import geocoder
from eloue.products.forms import FacetedSearchForm
from eloue.products.models import ProductRelatedMessage, MessageThread
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
            'fallback': fallback
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
        Q(state=Booking.STATE.CLOSED)|Q(state=Booking.STATE.CLOSING)
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
                    form.save()
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
    if booking.state not in (Booking.STATE.CLOSING, Booking.STATE.CLOSED):
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
            form.save()
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
    form = FacetedSearchForm()
    patron = get_object_or_404(Patron.on_site, slug=slug)
    return object_list(
        request, patron.products.all(), page=page, 
        paginate_by=PAGINATE_PRODUCTS_BY, 
        template_name='accounts/patron_detail.html', 
        template_object_name='product', extra_context={
            'form': form, 'patron': patron, 
            'borrowercomments': BorrowerComment.objects.filter(booking__owner=patron)[:4]
        }
    )


@login_required
def patron_edit(request, *args, **kwargs):
    paypal = request.GET.get('paypal', False)
    redirect_path = request.REQUEST.get('next', '')
    patron = request.user

    patron_dict = model_to_dict(patron)
    
    patron_edit_form = PatronEditForm(request.POST or None, request.FILES or None, instance=patron, initial=patron_dict, prefix='patronEdit')
    more_info_edit_form = MoreInformationForm(request.POST or None, instance=patron, initial=patron_dict, prefix='moreInfoEdit')

    forms = [patron_edit_form, more_info_edit_form]
    is_multipart = any([form.is_multipart() for form in forms])

    if patron_edit_form.is_valid() and more_info_edit_form.is_valid():
        for form in forms:
            patron = form.save()
        if paypal:
            is_valid = patron.is_valid
            is_confirmed = patron.is_confirmed
            if patron.is_valid and patron.is_confirmed:
                protocol = 'https' if USE_HTTPS else 'http'
                domain = Site.objects.get_current().domain
                if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
                    redirect_path = reverse('dashboard')
                return_url = "%s://%s%s?paypal=true" % (protocol, domain, redirect_path)
                messages.success(request, _(u"Vos informations ont bien été modifiées et votre compte paypal est valide"))    
                return redirect_to(request, return_url)
            else:
                if not is_valid:
                    messages.error(request, _(u"Votre Paypal compte est invalide, veuillez modifier votre nom ou prénom ou email paypal"))
                if not is_confirmed:
                    messages.error(request,  _(u"Vérifiez que vous avez bien répondu à l'email d'activation de Paypal"))
        elif request.POST:
            messages.success(request, _(u"Vos informations ont bien été modifiées")) 

        return redirect(reverse('patron_edit'))
    
    return direct_to_template(
        request, 'accounts/patron_edit.html', 
        extra_context={
            'forms': forms, 
            'patron': request.user,
            'is_multipart': is_multipart
        }
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
    from eloue.accounts.forms import AccountCreditCard
    from eloue.accounts.models import CreditCard
    try:
        instance = request.user.creditcard
    except CreditCard.DoesNotExist:
        instance = CreditCard(holder=request.user)
    if request.method == 'POST':
        form = AccountCreditCard(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(patron_edit_credit_card)
    else:
        form = AccountCreditCard(data=None, instance=instance)
    return render_to_response(
        template_name='accounts/patron_edit_credit_card.html', 
        dictionary={'form': form}, context_instance=RequestContext(request))

@login_required
def patron_edit_rib(request):
    from eloue.accounts.forms import RIBForm
    if request.method == 'POST':
        form = RIBForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(request.GET.get('next') or patron_edit_rib)
    else:
        form = RIBForm(data=None, instance=request.user)
    return render_to_response(
        template_name='accounts/patron_edit_rib.html',
        dictionary={'form': form}, context_instance=RequestContext(request)
    )

@login_required
def patron_edit_addresses(request):
    from eloue.accounts.forms import AddressFormSet
    if request.POST:
        formset = AddressFormSet(request.POST, instance=request.user)
        if formset.is_valid():
            formset.save()
            messages.success(request, _(u"Vos addresses ont bien été modifiées"))
            return redirect('eloue.accounts.views.patron_edit_addresses')
    else:
        formset = AddressFormSet(instance=request.user)
    return render_to_response('accounts/patron_edit_addresses.html', dictionary={'formset': formset}, context_instance=RequestContext(request))

@login_required
def patron_paypal(request):
    form = PatronPaypalForm(request.POST or None,
        initial={'paypal_email': request.user.email}, instance=request.user)
    redirect_path = request.REQUEST.get('next', '')
    booking_id = redirect_path.split("/")[-2]
    from eloue.rent.models import Booking
    booking = Booking.objects.get(uuid=booking_id)
    if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
        redirect_path = reverse('dashboard')
    if form.is_valid():
        
        patron = form.save()
        protocol = 'https' if USE_HTTPS else 'http'
        domain = Site.objects.get_current().domain
        return_url = "%s://%s%s?paypal=true" % (protocol, domain, redirect_path)
        profile_edit_url = "%s://%s%s?next=%s&paypal=true"% (protocol, domain, reverse('patron_edit'), redirect_path)
        
        if form.paypal_exists:
            is_valid = patron.is_valid
            is_confirmed = patron.is_confirmed
            if is_valid and is_confirmed:
                messages.success(request, _(u"Votre compte paypal est valide"))
                return redirect_to(request, return_url)
            else:
                if not is_valid:
                    messages.error(request, _(u"Votre Paypal compte est invalide, veuillez modifier votre nom ou prénom ou email paypal"))
                if not is_confirmed:
                    messages.error(request,  _(u"Vérifiez que vous avez bien répondu à l'email d'activation de Paypal"))
                return redirect_to(request, profile_edit_url)
        else: 
            paypal_redirect = patron.create_account(return_url=return_url)
            if paypal_redirect:
                return redirect_to(request, paypal_redirect)
        patron.paypal_email = None
        patron.save()
        messages.error(request, _(u"Nous n'avons pas pu créer votre compte paypal"))
    return direct_to_template(request, 'accounts/patron_paypal.html', extra_context={'form': form, 'next': redirect_path})


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
    queryset = request.user.bookings.filter(state=Booking.STATE.AUTHORIZED)
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Demandes de réservation'},
        template_name='accounts/owner_booking.html'
    )

@login_required
def owner_booking_pending(request, page=None):
    queryset = request.user.bookings.filter(state=Booking.STATE.PENDING)
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations à venir'},
        template_name='accounts/owner_booking.html'
    )

@login_required
def owner_booking_ongoing(request, page=None):
    queryset = request.user.bookings.filter(state=Booking.STATE.ONGOING)
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations en cours'},
        template_name='accounts/owner_booking.html'
    )

@login_required
def owner_booking_history(request, page=None):
    queryset = request.user.bookings.exclude(
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
        template_name='accounts/owner_booking.html')

@login_required
def owner_history(request, page=None):
    queryset = request.user.bookings.filter(state__in=[Booking.STATE.CLOSED, Booking.STATE.REJECTED])
    return object_list(request, queryset, page=page, paginate_by=10, template_name='accounts/owner_history.html',
        template_object_name='booking')


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
    queryset = request.user.rentals.filter(state=Booking.STATE.ONGOING)
    return object_list(
        request, queryset, page=page, paginate_by=10,
        extra_context={'title_page': u'Réservations en cours'},
        template_name='accounts/borrower_booking.html')

@login_required
def borrower_booking_pending(request, page=None):
    queryset = request.user.rentals.filter(state=Booking.STATE.PENDING)
    return object_list(
        request, queryset, page=page, paginate_by=10, 
        extra_context={'title_page': u'Réservations à venir'},
        template_name='accounts/borrower_booking.html')

@login_required
def borrower_booking_authorized(request, page=None):
    queryset = request.user.rentals.filter(state=Booking.STATE.AUTHORIZED)
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
        template_name='accounts/borrower_booking.html')

@mobify
def contact(request):
    form = ContactForm(request.POST or None)
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
        except (BadHeaderError, smtplib.SMTPException, socket.error):
            messages.error(request, _(u"Erreur lors de l'envoi du message"))
    return direct_to_template(request, 'accounts/contact.html', extra_context={'form': ContactForm()})

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

