# -*- coding: utf-8 -*-
import datetime
import qsstats

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Avg, Sum, Q, Count

from eloue.accounts.models import Patron
from eloue.products.models import Product, CarProduct, RealEstateProduct, Category
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

def top_patron_city(request):
	cities = Patron.objects.extra(tables=['accounts_address'], where=['"accounts_patron"."default_address_id" = "accounts_address"."id"'], select={'city': 'lower(accounts_address.city)'}).values('city').annotate(Count('id')).order_by('-id__count')[:50]

   	return render_to_response("reporting/admin/top_city.html",
   		{},
   		RequestContext(request, {'cities': cities}),
   	)

def top_booking_patron(request):
	patrons = Patron.objects.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')[:30]

	return render_to_response("reporting/admin/top_patron.html",
		{},
		RequestContext(request, {'patrons': patrons}),
	)

def top_product_city(request):
	cities = Product.objects.extra(tables=['accounts_address'], where=['"products_product"."address_id" = "accounts_address"."id"'], select={'city': 'lower(accounts_address.city)'}).values('city').annotate(Count('id')).order_by('-id__count')[:50]

	return render_to_response("reporting/admin/top_city.html",
   		{},
   		RequestContext(request, {'cities': cities}),
   	)


def top_product_category(request):
	categories = Category.tree.annotate(num_products=Count('products')).order_by('-num_products')[:30]


	return render_to_response("reporting/admin/top_category.html",
   		{},
   		RequestContext(request, {'categories': categories}),
   	)


stats = staff_member_required(stats)
top_patron_city = staff_member_required(top_patron_city)
top_product_city = staff_member_required(top_product_city)
top_product_category = staff_member_required(top_product_category)
top_booking_patron = staff_member_required(top_booking_patron)