# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from rest_framework.decorators import link, action
from rest_framework.response import Response

import django_filters

from eloue.api.decorators import user_required
from eloue.api import viewsets, filters, mixins, exceptions

from payments.models import PayboxDirectPlusPaymentInformation
from accounts.serializers import CreditCardSerializer, BookingPayCreditCardSerializer

from .forms import SinisterForm
from .models import Sinister
from .choices import BOOKING_STATE
from . import serializers, models


USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


# REST API 2.0


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

    @link()
    def contract(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(state__in=[BOOKING_STATE.PENDING, BOOKING_STATE.ONGOING, BOOKING_STATE.ENDED, BOOKING_STATE.CLOSED, BOOKING_STATE.INCIDENT])
        obj = self.get_object(queryset=queryset)
        content = obj.product.subtype.contract_generator(obj).getvalue()
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=contrat.pdf'
        return response

    @action(methods=['put'])
    @user_required(attname='borrower')
    def pay(self, request, *args, **kwargs):
        obj = self.get_object()
        data = request.DATA
        try:
            credit_card = data['credit_card']
            context = self.get_serializer_context()
            context.update({'suppress_exception': True})
            serializer = BookingPayCreditCardSerializer(data=data, context=context)
            credit_card = serializer.fields['creditcard'].from_native(credit_card)
            credit_card.cvv = ''
        except (KeyError, ValidationError):
            serializer = CreditCardSerializer(data=data, context=self.get_serializer_context())
            if not serializer.is_valid():
                raise exceptions.ValidationException(serializer.errors)
            credit_card = serializer.save()

        if not settings.TEST_MODE:
            payment = PayboxDirectPlusPaymentInformation.objects.create(creditcard=credit_card)
            obj.payment = payment
        return self._perform_transition(request, instance=obj, action='preapproval', cvv=credit_card.cvv)

    @action(methods=['put'])
    @user_required(attname='owner')
    def accept(self, request, *args, **kwargs):
        return self._perform_transition(request, action='accept')

    @action(methods=['put'])
    @user_required(attname='owner')
    def reject(self, request, *args, **kwargs):
        return self._perform_transition(request, action='reject')

    @action(methods=['put'])
    @user_required(attname='borrower')
    def cancel(self, request, *args, **kwargs):
        return self._perform_transition(request, action='cancel', source=request.user)

    @action(methods=['put'])
    @user_required(attname='owner')
    def close(self, request, *args, **kwargs):
        return self._perform_transition(request, action='close', source=request.user)

    @action(methods=['put'])
    def incident(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(state__in=[BOOKING_STATE.ONGOING, BOOKING_STATE.ENDED, BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED])
        obj = self.get_object(queryset=queryset)
        form = SinisterForm(
            request.DATA.copy(),
            instance=Sinister(
                booking=obj, patron=request.user, product=obj.product
            )
        )
        if not form.is_valid():
            raise exceptions.ValidationException(form.errors)
        sinister = form.save() # save Sinister object
        return self._perform_transition(request, action='incident', source=request.user, description=sinister.description)

    def _perform_transition(self, request, action=None, instance=None, **kwargs):
        if instance is None:
            instance = self.get_object()
        serializer = serializers.BookingActionSerializer(instance=instance, data={'action': action}, context=self.get_serializer_context())
        if not serializer.is_valid():
            raise exceptions.ValidationException(serializer.errors)
        serializer.save(**kwargs)
        return Response({'detail': _(u'Transition performed')})

    def paginate_queryset(self, queryset, page_size=None):
        self.object_list = queryset.model.on_site.active(queryset)
        return super(BookingViewSet, self).paginate_queryset(self.object_list, page_size=page_size)


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


class SinisterViewSet(mixins.SetOwnerMixin, viewsets.ImmutableModelViewSet):
    """
    API endpoint that allows sinisters to be viewed or edited.
    """
    model = models.Sinister
    queryset = models.Sinister.objects.select_related('booking__owner', 'booking__borrower')
    serializer_class = serializers.SinisterSerializer
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    owner_field = ('patron', 'booking__owner', 'booking__borrower')
    filter_fields = ('patron', 'booking', 'product')
