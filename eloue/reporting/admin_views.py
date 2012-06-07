# -*- coding: utf-8 -*-
import datetime
import qsstats

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Avg, Sum, Q, Count

from eloue.accounts.models import Patron
from eloue.products.models import Product, CarProduct, RealEstateProduct
from eloue.rent.models import Booking



def stats(request):
	data = {}

	booking_transaction_list = [Booking.STATE.PENDING, Booking.STATE.ONGOING, Booking.STATE.ENDED, Booking.STATE.INCIDENT, Booking.STATE.CLOSING, Booking.STATE.CLOSED]

	qss_parameters_list = {
		'patrons': (Patron.objects.all(), 'date_joined'),
		'patrons_private': (Patron.objects.filter(Q(is_professional=False) | Q(is_professional=None)) , 'date_joined'),
		'patrons_professionnal': (Patron.objects.filter(is_professional=True), 'date_joined'),
		'products': (Product.objects.all(), 'created_at'),
		'car_product': (CarProduct.objects.all(), 'created_at'),
		'real_estate_product': (RealEstateProduct.objects.all(), 'created_at'),
		'other_item_product': (Product.objects.filter(carproduct=None).filter(realestateproduct=None), 'created_at'),
		'asked_booking': (Booking.objects.all(), 'created_at', Count('uuid')),
		'booking': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Count('uuid')),
		'car_booking': (Booking.objects.filter(state__in=booking_transaction_list).filter(~Q(product__carproduct=None)), 'created_at', Count('uuid')),
		'real_estate_booking': (Booking.objects.filter(state__in=booking_transaction_list).filter(~Q(product__realestateproduct=None)), 'created_at', Count('uuid')),
		'other_item_booking': (Booking.objects.filter(state__in=booking_transaction_list).filter(Q(product__realestateproduct=None, product__carproduct=None)), 'created_at', Count('uuid')),
		'average_total_amount_asked_booking': (Booking.objects.all(), 'created_at', Avg('total_amount')),
		'average_total_amount_booking': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Avg('total_amount')),
		'sum_total_amount_asked_booking': (Booking.objects.all(), 'created_at', Sum('total_amount')),
		'sum_total_amount_booking': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Sum('total_amount')),
		'need_assurancy_asked_booking': (Booking.objects.filter(Q(product__category__need_insurance=True)), 'created_at', Count('uuid')),
		'need_assurancy_booking': (Booking.objects.filter(state__in=booking_transaction_list).filter(Q(product__category__need_insurance=True)), 'created_at', Count('uuid')),
		'incident_declaration': (Booking.objects.filter(state__in=[Booking.STATE.INCIDENT]), 'created_at', Count('uuid')),
	}

	for key, value in qss_parameters_list.items():
		data[key] = qsstats.QuerySetStats(*value).time_series(datetime.date(2012, 1, 1), datetime.date(2012, 12, 31), interval='months')


	return render_to_response(
        "reporting/admin/stats.html",
		{},
		RequestContext(request, {'stats': data}),
    )

stats = staff_member_required(stats)