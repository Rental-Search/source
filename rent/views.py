# -*- coding: utf-8 -*-
import logbook
import urllib
from datetime import datetime, date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser
from django.template import RequestContext

from accounts.forms import EmailAuthenticationForm
from accounts.utils import viva_check_phone
from payments.models import PayboxDirectPlusPaymentInformation
from products.models import Product
from products.choices import UNIT
from rent.forms import BookingForm, BookingAcceptForm, PreApprovalIPNForm, PayIPNForm, SinisterForm
from rent.models import Booking, ProBooking
from rent.wizard import BookingWizard, PhoneBookingWizard
from rent.utils import timesince
from rent.choices import BOOKING_STATE

from eloue.utils import currency, json
from eloue.decorators import ownership_required, validate_ipn, secure_required, mobify

log = logbook.Logger('eloue.rent')
USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


@require_POST
@csrf_exempt
@validate_ipn
def preapproval_ipn(request):
    form = PreApprovalIPNForm(request.POST)
    if form.is_valid():
        booking = Booking.objects.get(preapproval_key=form.cleaned_data['preapproval_key'])
        if form.cleaned_data['approved'] and form.cleaned_data['status'] == 'ACTIVE':
            # Changing state
            booking.state = BOOKING_STATE.AUTHORIZED # FIXME: must use actions instead of changing state directly
            booking.borrower.paypal_email = form.cleaned_data['sender_email']
            booking.borrower.save()
            # Sending email
            booking.send_ask_email()
        else:
            booking.state = BOOKING_STATE.REJECTED # FIXME: must use actions instead of changing state directly
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
            booking.state = BOOKING_STATE.ONGOING # FIXME: must use actions instead of changing state directly
        else:  # FIXME : naïve
            booking.state = BOOKING_STATE.CLOSED # FIXME: must use actions instead of changing state directly
        booking.save()
    return HttpResponse()


def product_occupied_date(request, slug, product_id):
    product = get_object_or_404(Product.on_site, pk=product_id)
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, (datetime, date)) else None
    if 'year' in request.GET and 'month' in request.GET:
        return HttpResponse(
            json.dumps(
                product.monthly_availability(request.GET['year'], request.GET['month']),
                default=dthandler), 
            content_type='application/json'
        )
    else:
        return HttpResponse('[]', content_type='application/json')


def get_booking_price_from_form(form):
    product = form.instance.product
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
          'quantity': max_available if quantity > max_available else quantity,
        }
        if quantity > max_available:
            response_dict.setdefault('warnings', []).append(_(u'Quantité disponible à cette période: %s') % max_available)
    else:
        max_available = getattr(form, 'max_available', product.quantity)
        try:
            price_unit = product.prices.filter(unit=1)[0]
            response_dict = {
              'unit_name': UNIT[1][1],
              'unit_value': smart_str(currency(price_unit.amount)),
              'max_available': max_available,
              'quantity': 1,
            }
        except:
            response_dict = {}
    return response_dict


@require_GET
@never_cache
def booking_price(request, slug, product_id):
    if not request.is_ajax():
        return HttpResponseNotAllowed(['GET', 'XHR'])

    product = get_object_or_404(Product.on_site, pk=product_id)
    form = BookingForm(request.GET, prefix="0", instance=Booking(product=product))
    response_dict = get_booking_price_from_form(form)

    # add errors if the form is invalid
    if not form.is_valid():
        response_dict['errors'] = form.errors.values()

    # add 'select_list' field with values for the quantity selection box
    max_available = response_dict.get('max_available', None)
    selected = response_dict.pop('quantity', None)
    if max_available and selected:
        select_options = [{'value': x, 'selected': x == selected} for x in xrange(1, 1 + max_available)]
        response_dict['select_list'] = select_options

    return HttpResponse(json.dumps(response_dict), content_type='application/json')


@require_GET
def get_availability(request, product_id, year, month):
    product = get_object_or_404(Product.on_site, pk=product_id)
    availability = product.daily_available(year, month)
    return HttpResponse(json.dumps(availability), content_type='application/json')


@mobify
@never_cache
@secure_required
def booking_create_redirect(request, *args, **kwargs):
    product = get_object_or_404(Product.on_site, pk=kwargs['product_id'])
    return redirect(product)


@mobify
@never_cache
@secure_required
def booking_create(request, *args, **kwargs):
    product = get_object_or_404(Product.on_site.active().select_related(
        'address', 'category', 'owner', 'owner__default_address', 
        'carproduct', 'realestateproduct'
        ), pk=kwargs['product_id']).subtype
    if product.slug != kwargs['slug']:
        return redirect(product, permanent=True)
    wizard = BookingWizard([BookingForm, EmailAuthenticationForm,])
    return wizard(request, product, product.subtype, *args, **kwargs)

@mobify
@never_cache
@secure_required
def phone_create(request, *args, **kwargs):
    product = get_object_or_404(Product.on_site.active().select_related(
        'address', 'category', 'owner', 'owner__default_address', 
        'carproduct', 'realestateproduct'
        ), pk=kwargs['product_id']).subtype

    # get call details by number and request parameters (e.g. REMOTE_ADDR)
    tags = viva_check_phone(product.phone.number, request=request)
    number = tags['numero']
    
    num = lambda s: ' '.join(' '.join(s[i:i+2] for i in range(0, len(s), 2)).split())

    wizard = PhoneBookingWizard([BookingForm, EmailAuthenticationForm,])


    return wizard(request, product, num(number), product.subtype, *args, **kwargs)

from django.views.generic import DetailView
from django.utils.decorators import method_decorator
class BookingSuccess(DetailView):
    @method_decorator(login_required)
    @method_decorator(ownership_required(model=Booking, object_key='booking_id', ownership=['borrower']))
    def dispatch(self, *args, **kwargs):
        return super(BookingSuccess, self).dispatch(*args, **kwargs)

    queryset = Booking.on_site.all()
    pk_url_kwarg = 'booking_id'
    template_name = 'rent/booking_success.html'
    context_object_name = 'booking'


class BookingFailure(DetailView):
    @method_decorator(login_required)
    @method_decorator(ownership_required(model=Booking, object_key='booking_id', ownership=['borrower']))
    def dispatch(self, *args, **kwargs):
        return super(BookingFailure, self).dispatch(*args, **kwargs)

    queryset = Booking.on_site.all()
    pk_url_kwarg = 'booking_id'
    template_name = 'rent/booking_failure.html'
    context_object_name = 'booking'


class BookingDetail(DetailView):
    @method_decorator(login_required)
    @method_decorator(ownership_required(model=Booking, object_key='booking_id', ownership=['borrower', 'owner']))
    def dispatch(self, *args, **kwargs):
        return super(BookingDetail, self).dispatch(*args, **kwargs)

    queryset = Booking.on_site.all()
    pk_url_kwarg = 'booking_id'
    template_name = 'rent/booking_detail.html'
    context_object_name = 'booking'


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_contract(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, state=BOOKING_STATE.PENDING)
    content = booking.product.subtype.contract_generator(booking).getvalue()
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=contrat.pdf'
    return response

@login_required
@require_POST
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_accept(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, state=BOOKING_STATE.AUTHORIZED)
    if booking.started_at < datetime.now():
        booking.expire()
        booking.save()
        messages.error(request, _(u"Votre demande est dépassée"))
    else:
        if not request.user.rib:
            response = redirect('patron_edit_rib')
            response['Location'] += '?' + urllib.urlencode({'accept': booking.pk.hex})
            messages.error(
                request, 
                _(u"Avant l'acceptation de la demande, "
                    u"veuillez saisir votre RIB."))
            return response
        form = BookingAcceptForm(request.POST or None, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.accept()
            booking.save()
            messages.success(request, _(u"La demande de location a été acceptée"))
            GoalRecord.record('rent_object_accepted', WebUser(request))
        else:
            messages.error(request, _(u"La demande de location n'a pu être acceptée"))
    return redirect(booking)

@login_required
@require_POST
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_reject(request, booking_id):
    booking = get_object_or_404(Booking.on_site, pk=booking_id, state=BOOKING_STATE.AUTHORIZED)
    if booking.started_at < datetime.now():
        booking.expire()
        booking.save()
        messages.error(request, _(u"Votre demande est dépassée"))
    else:
        booking.reject()
        booking.save()
        GoalRecord.record('rent_object_rejected', WebUser(request))
        messages.success(request, _(u"Cette réservation a bien été refusée"))
    return redirect(booking)


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_read(request, booking_id):
    booking = get_object_or_404(Booking.on_site, pk=booking_id, state=BOOKING_STATE.PROFESSIONAL)
    assert isinstance(booking, ProBooking)
    if request.method == "POST":
        booking.accept() # FIXME: rename to read
        booking.save()
        messages.success(request, _(u"Cette réservation a bien été marqué comme lu"))
    return redirect(booking)


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['borrower'])
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking.on_site, pk=booking_id, state__in=[BOOKING_STATE.AUTHORIZING, BOOKING_STATE.AUTHORIZED, BOOKING_STATE.PENDING])
    if request.POST:
        booking.cancel(source=request.user)
        booking.save()
        messages.success(request, _(u"Cette réservation a bien été annulée"))
    return redirect(booking)


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner'])
def booking_close(request, booking_id):
    booking = get_object_or_404(Booking.on_site, pk=booking_id, state=BOOKING_STATE.ENDED)
    if request.POST:
        booking.close()
        booking.save()
        messages.success(request, _(u"Cette réservation a bien été cloturée. Si vous voulez vous pouvez ajouter un commentaire et une note sur le déroulement de la location."))
        return redirect(reverse('comments')+'#'+booking.pk.hex)
    return redirect(booking)


@login_required
@ownership_required(model=Booking, object_key='booking_id', ownership=['owner', 'borrower'])
def booking_incident(request, booking_id):
    booking = get_object_or_404(Booking.on_site, pk=booking_id, state__in=[BOOKING_STATE.ONGOING, BOOKING_STATE.ENDED, BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED])
    from rent.models import Sinister
    if request.method == "POST":
        form = SinisterForm(
            request.POST,
            instance=Sinister(
                booking=booking, patron=request.user, product=booking.product
            )
        )
        if form.is_valid():
            form.save() # save Sinister object
            booking.incident(request.user, form.cleaned_data['description'])
            booking.save()
            messages.success(request, _(u'Nous avons bien pris en compte la déclaration de l\'incident. Nous vous contacterons rapidement.'))
            return redirect('booking_detail', booking_id=booking_id)
    else:
        form = SinisterForm()
    return render_to_response(
        template_name='rent/booking_incident.html', 
        dictionary={'booking': booking, 'form': form}, 
        context_instance=RequestContext(request)
    )


# REST API 2.0

from rest_framework import status
from rest_framework.decorators import link, action
from rest_framework.response import Response
import django_filters

from rent import serializers, models
from eloue.api import viewsets, filters, mixins
from accounts.serializers import CreditCardSerializer, BookingPayCreditCardSerializer

class BookingFilterSet(filters.FilterSet):
    author = filters.MultiFieldFilter(name=('owner', 'borrower'))

    class Meta:
        model = models.Booking
        fields = (
            'state', 'owner', 'borrower', 'product',
            'started_at', 'ended_at', 'total_amount', 'created_at', 'canceled_at'
        )

class BookingViewSet(mixins.SetOwnerMixin, viewsets.ImmutableModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    permission_classes = tuple()
    queryset = models.Booking.on_site.all()
    serializer_class = serializers.BookingSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = ('borrower', 'owner')
    filter_class = BookingFilterSet
    ordering_fields = ('started_at', 'ended_at', 'state', 'total_amount', 'created_at', 'canceled_at')

    @link()
    def available_transitions(self, request, *args, **kwargs):
        obj = self.get_object()
        transitions = obj.get_available_user_state_transitions(request.user)
        res = {transition.method.__name__: transition.target for transition in transitions}
        return Response(dict(transitions=res))

    @action(methods=['put'])
    def pay(self, request, *args, **kwargs):
        data = request.DATA
        try:
            credit_card = data['credit_card']
            serializer = BookingPayCreditCardSerializer(
                data=data, context={'request': request, 'suppress_exception': True}
            )
            credit_card = serializer.fields['creditcard'].from_native(credit_card)
            credit_card.cvv = ''
        except (KeyError, ValidationError):
            serializer = CreditCardSerializer(data=data, context={'request': request})
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            credit_card = serializer.save()

        payment = PayboxDirectPlusPaymentInformation.objects.create(creditcard=credit_card)
        booking = self.get_object()
        booking.payment = payment
        booking.save()
        return self._perform_transition(request, action='preapproval', cvv=credit_card.cvv)

    @action(methods=['put'])
    def accept(self, request, *args, **kwargs):
        return self._perform_transition(request, action='accept')

    @action(methods=['put'])
    def reject(self, request, *args, **kwargs):
        return self._perform_transition(request, action='reject')

    @action(methods=['put'])
    def cancel(self, request, *args, **kwargs):
        return self._perform_transition(request, action='cancel')

    def _perform_transition(self, request, action=None, **kwargs):
        serializer = serializers.BookingActionSerializer(instance=self.get_object(), data={'action': action}, context={'request': request})
        if serializer.is_valid():
            serializer.save(**kwargs)
            return Response({'detail': _(u'Transition performed')})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CommentFilterSet(filters.FilterSet):
    rate = django_filters.ChoiceFilter(name='note', choices=serializers.CommentSerializer.base_fields['rate'].choices)
    author = filters.MultiFieldFilter(name=('booking__owner', 'booking__borrower'))

    class Meta:
        model = models.Comment
        fields = ('booking',)

class CommentViewSet(viewsets.NonEditableModelViewSet):
    """
    API endpoint that allows transaction comments to be viewed or edited.
    """
    model = models.Comment
    queryset = models.Comment.objects.select_related('booking__owner', 'booking__borrower')
    serializer_class = serializers.CommentSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = ('booking__owner', 'booking__borrower')
    filter_class = CommentFilterSet
    ordering_fields = ('note', 'created_at')
    public_actions = ('retrieve',)

class SinisterViewSet(viewsets.ImmutableModelViewSet):
    """
    API endpoint that allows sinisters to be viewed or edited.
    """
    model = models.Sinister
    serializer_class = serializers.SinisterSerializer
    filter_backends = (filters.OwnerFilter, filters.OrderingFilter)
    filter_fields = ('patron', 'booking', 'product')
