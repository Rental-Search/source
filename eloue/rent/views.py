# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template, redirect_to

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.decorators import ownership_required, validate_ipn, secure_required, mobify
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.products.models import Product
from eloue.rent.forms import BookingForm, BookingConfirmationForm, BookingStateForm, PreApprovalIPNForm, PayIPNForm, IncidentForm
from eloue.rent.models import Booking
from eloue.rent.wizard import BookingWizard

log = logbook.Logger('eloue.rent')


@require_POST
@csrf_exempt
@validate_ipn
def preapproval_ipn(request):
    form = PreApprovalIPNForm(request.POST)
    if form.is_valid():
        booking = Booking.objects.get(preapproval_key=form.cleaned_data['preapproval_key'])
        if form.cleaned_data['approved'] and form.cleaned_data['status'] == 'ACTIVE':
            # Changing state
            booking.state = Booking.STATE.AUTHORIZED
            booking.borrower.paypal_email = form.cleaned_data['sender_email']
            booking.borrower.save()
            # Sending email
            booking.send_ask_email()
        else:
            booking.state = Booking.STATE.REJECTED
        booking.save()
    return HttpResponse()


@require_POST
@csrf_exempt
@validate_ipn
def pay_ipn(request):
    form = PayIPNForm(request.POST)
    if form.is_valid():
        booking = Booking.objects.get(pay_key=form.cleaned_data['pay_key'])
        if form.cleaned_data['action_type'] == 'PAY_PRIMARY' and form.cleaned_data['status'] == 'INCOMPLETE':
            booking.state = Booking.STATE.ONGOING
        else: # FIXME : naïve
            booking.state = Booking.STATE.CLOSED
        booking.save()
    return HttpResponse()


@require_GET
def booking_price(request, slug, product_id):
    if not request.is_ajax():
        return HttpResponseNotAllowed(['GET', 'XHR'])
    product = get_object_or_404(Product, pk=product_id)
    form = BookingForm(request.GET, prefix="0", instance=Booking(product=product))
    if form.is_valid():
        duration = timesince(form.cleaned_data['started_at'], form.cleaned_data['ended_at'])
        total_price = smart_str(form.cleaned_data['total_amount'])
        return HttpResponse(simplejson.dumps({'duration': duration, 'total_price': total_price}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'errors': form.errors.values()}), mimetype='application/json')


@mobify
@never_cache
@secure_required
def booking_create(request, *args, **kwargs):
    product = get_object_or_404(Product, pk=kwargs['product_id'])
    if product.slug != kwargs['slug']:
        return redirect_to(request, product.get_absolute_url())
    wizard = BookingWizard([BookingForm, EmailAuthenticationForm, BookingConfirmationForm])
    return wizard(request, *args, **kwargs)


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['borrower'])
def booking_success(request, booking_id):
    return object_detail(request, queryset=Booking.objects.all(), object_id=booking_id,
        template_name='rent/booking_success.html', template_object_name='booking')


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['borrower'])
def booking_failure(request, booking_id):
    return object_detail(request, queryset=Booking.objects.all(), object_id=booking_id,
        template_name='rent/booking_failure.html', template_object_name='booking')


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_detail(request, booking_id):
    paypal = request.GET.get('paypal', False)
    return object_detail(request, queryset=Booking.objects.all(), object_id=booking_id,
        template_name='rent/booking_detail.html', template_object_name='booking', extra_context={'paypal': paypal})


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_accept(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if not booking.owner.has_paypal():
        return redirect_to(request, "%s?next=%s" % (reverse('patron_paypal'), booking.get_absolute_url()))
    form = BookingStateForm(request.POST or None,
        initial={'state': Booking.STATE.PENDING},
        instance=booking)
    if form.is_valid():
        booking = form.save()
        booking.send_acceptation_email()
        GoalRecord.record('rent_object_accepted', WebUser(request))
        booking.save()
    return redirect_to(request, "%s?paypal=true" % booking.get_absolute_url())


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
        messages.success(request,_(u"Cette réservation a bien été refusée"))
    messages.error(request, _(u"Cette réservation n'a pu être refusée"))
    return redirect_to(request, booking.get_absolute_url())


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.POST:
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
        booking.pay()
        booking.send_closed_email()
        messages.success(request, _(u"Cette réservation a bien été cloturée"))
    messages.error(request, _(u"Cette réservation n'a pu être cloturée"))
    return redirect_to(request, booking.get_absolute_url())


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_incident(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    form = IncidentForm(request.POST or None)
    if form.is_valid():
        send_mail(u"Déclaration d'incident", form.cleaned_data['message'], settings.DEFAULT_FROM_EMAIL, ['incident@e-loue.com'])
        booking.state = Booking.STATE.INCIDENT
        booking.save()
    return direct_to_template(request, 'rent/booking_incident.html', extra_context={'booking': booking, 'form': form})

