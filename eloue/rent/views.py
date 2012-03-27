# -*- coding: utf-8 -*-
import logbook
import urllib
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template, redirect_to
from django.db.models import Q
from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser
from django.contrib.sites.models import Site


from eloue.accounts.models import CreditCard
from eloue.decorators import ownership_required, validate_ipn, secure_required, mobify
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.products.models import Product, PAYMENT_TYPE, UNIT
from eloue.rent.forms import BookingForm, BookingConfirmationForm, BookingStateForm, PreApprovalIPNForm, PayIPNForm, IncidentForm
from eloue.rent.models import Booking
from eloue.rent.wizard import BookingWizard
from eloue.utils import currency
from datetime import datetime, timedelta
from eloue.rent.utils import get_product_occupied_date, timesince

log = logbook.Logger('eloue.rent')
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


def product_occupied_date(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)
    bookings = Booking.objects.filter(product=product).filter(Q(state="pending")|Q(state="ongoing"))
    dates = get_product_occupied_date(bookings)
    formated_date = [str(d.year) + '-' + str(d.month) + '-' + str(d.day) for d in dates]
    formated_date = list(set(formated_date))
    return HttpResponse(simplejson.dumps(formated_date), mimetype='application/json')


@require_GET
def booking_price(request, slug, product_id):

    def generate_select_list(n, selected):
        select_options = [{'value': x, 'selected': x==selected} for x in xrange(1, 1 + n)]
        return select_options

    if not request.is_ajax():
        return HttpResponseNotAllowed(['GET', 'XHR'])
    product = get_object_or_404(Product.on_site, pk=product_id)
    form = BookingForm(request.GET, prefix="0", instance=Booking(product=product))
    
    if form.is_valid():
        duration = timesince(form.cleaned_data['started_at'], form.cleaned_data['ended_at'])
        total_price = smart_str(currency(form.cleaned_data['total_amount']))
        price_unit = form.cleaned_data['price_unit']
        quantity = form.cleaned_data['quantity']
        max_available = form.max_available
        if quantity is None and max_available > 0:
            quantity = 1
        response_dict = {
          'duration': duration,
          'total_price': total_price, 
          'unit_name': UNIT[price_unit][1], 
          'unit_value': smart_str(currency(product.prices.filter(unit=price_unit)[0].amount)), 
          'max_available': max_available, 
          'select_list': generate_select_list(max_available, selected=quantity) 
        }
        if quantity > max_available:
            response_dict.setdefault('warnings', []).append('Quantité disponible à cette période: %s' % max_available)
            response_dict['select_list'] = generate_select_list(max_available, selected=max_available)
        else:
            response_dict['select_list'] = generate_select_list(max_available, selected=quantity)
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
    else:
        max_available = getattr(form, 'max_available', product.quantity)
        price_unit = product.prices.filter(unit=1)[0]
        response_dict = {
          'errors': form.errors.values(), 
          'unit_name': UNIT[1][1], 
          'unit_value': smart_str(currency(price_unit.amount)), 
          'max_available': max_available, 
          'select_list': generate_select_list(max_available, selected=1)
        }
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

@require_GET
def get_availability(request, product_id, year, month):
    product = get_object_or_404(Product.on_site, pk=product_id)
    availability = product.daily_available(year, month)
    return HttpResponse(simplejson.dumps(availability), mimetype='application/json')
    
@mobify
@never_cache
@secure_required
def booking_create_redirect(request, *args, **kwargs):
    product = get_object_or_404(Product.on_site, pk=kwargs['product_id'])
    return redirect_to(request, product.get_absolute_url())

@mobify
@never_cache
@secure_required
def booking_create(request, *args, **kwargs):
    product = get_object_or_404(Product.on_site, pk=kwargs['product_id'])
    if product.slug != kwargs['slug']:
        return redirect(product)
    wizard = BookingWizard([BookingForm, EmailAuthenticationForm, BookingConfirmationForm])
    return wizard(request, *args, **kwargs)


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['borrower'])
def booking_success(request, booking_id):
    return object_detail(request, queryset=Booking.on_site.all(), object_id=booking_id,
        template_name='rent/booking_success.html', template_object_name='booking')


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['borrower'])
def booking_failure(request, booking_id):
    return object_detail(request, queryset=Booking.on_site.all(), object_id=booking_id,
        template_name='rent/booking_failure.html', template_object_name='booking')


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_detail(request, booking_id):
    paypal = request.GET.get('paypal', False)
    return object_detail(request, queryset=Booking.on_site.all(), object_id=booking_id,
        template_name='rent/booking_detail.html', template_object_name='booking', extra_context={'paypal': paypal})



def offer_accept(request, booking_id):
    return HttpResponseForbidden()
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.user == booking.offer_in_message.recipient:
        if booking.state == Booking.STATE.UNACCEPTED:
            booking.state = Booking.STATE.ACCEPTED_UNAUTHORIZED
            if request.user == booking.borrower:
                domain = Site.objects.get_current().domain
                protocol = "https" if USE_HTTPS else "http"
                booking.preapproval(
                    cancel_url="%s://%s%s" % (protocol, domain, reverse("booking_failure", args=[booking.pk.hex])),
                    return_url="%s://%s%s" % (protocol, domain, reverse("booking_success", args=[booking.pk.hex])),
                    ip_address=request.META['REMOTE_ADDR']
                )
            else:
                #send mail to borrower with paypal link
                pass
        else:
            #we should not be here
            pass
    else:
        return HttpResponseForbidden()

def offer_reject(request, booking_id):
    return HttpResponseForbidden()
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.user == booking.offer_in_message.recipient:
        if booking.state == Booking.STATE.UNACCEPTED:
            booking.state = Booking.STATE.REJECTED
        else:
            #we should not be here
            pass
    else:
        return HttpResponseForbidden()



@login_required
@require_POST
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_accept(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.started_at > datetime.datetime.now():
        booking.state = booking.STATE.OUTDATED
        booking.save()
    else:
        if not request.user.rib:
            response = redirect('patron_edit_rib')
            response['Location'] += '?' + urllib.urlencode({'next': booking.get_absolute_url()})
            return response
        booking.accept()
        GoalRecord.record('rent_object_accepted', WebUser(request))
    return redirect(booking)

@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_reject(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    form = BookingStateForm(request.POST or None,
        initial={'state': Booking.STATE.REJECTED},
        instance=booking)
    if form.is_valid():
        booking = form.save()
        booking.send_rejection_email()
        GoalRecord.record('rent_object_rejected', WebUser(request))
        messages.success(request, _(u"Cette réservation a bien été refusée"))
    messages.error(request, _(u"Cette réservation n'a pu être refusée"))
    return redirect_to(request, booking.get_absolute_url())


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST:
        booking.init_payment_processor()
        booking.cancel()
        booking.send_cancelation_email(source=request.user)
        messages.success(request, _(u"Cette réservation a bien été annulée"))
    messages.error(request, _(u"Cette réservation n'a pu être annulée"))
    return redirect_to(request, booking.get_absolute_url())


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_close(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST:
        booking.init_payment_processor()
        booking.pay()
        booking.send_closed_email()
        messages.success(request, _(u"Cette réservation a bien été cloturée"))
        messages.info(request, _(u"Cette réservation a bien été cloturée et le virement effectué. Si vous voulez vous pouvez ajouter une commentaire et une note sur le déroulement de la location."))
        return redirect(reverse('eloue.accounts.views.comments')+'#'+booking.pk.hex)
    messages.error(request, _(u"Cette réservation n'a pu être cloturée"))
    return redirect_to(request, booking.get_absolute_url())


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_incident(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    form = IncidentForm(request.POST or None)
    if form.is_valid():
        send_mail(u"Déclaration d'incident", form.cleaned_data['message'], settings.DEFAULT_FROM_EMAIL, ['contact@e-loue.com'])
        booking.state = Booking.STATE.INCIDENT
        booking.save()
    return direct_to_template(request, 'rent/booking_incident.html', extra_context={'booking': booking, 'form': form})

