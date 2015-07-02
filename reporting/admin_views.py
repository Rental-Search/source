# -*- coding: utf-8 -*-
import datetime
import qsstats

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Sum, Q, Count
from django.shortcuts import get_object_or_404

from django_messages.models import Message

from accounts.models import Patron
from products.models import Product, CarProduct, RealEstateProduct, Category
from rent.models import Booking, OwnerComment, BorrowerComment
from rent.choices import BOOKING_STATE


def stats(request):
	query_data = request.GET.copy()

	if query_data.get('year'):
		year = int(query_data.get('year'))
	else:
		year = int(2012)

	data = {}

	booking_transaction_list = [BOOKING_STATE.PENDING, BOOKING_STATE.ONGOING, BOOKING_STATE.ENDED, BOOKING_STATE.INCIDENT, BOOKING_STATE.CLOSING, BOOKING_STATE.CLOSED]

	qss_list = [
		{'title': 'products_pro', 'qss': (Product.objects.filter(owner__is_professional=True), 'created_at'), 'pos': 1},
		{'title': 'need_assurancy_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list).filter(Q(product__category__need_insurance=True)), 'created_at', Count('uuid')), 'pos': 2},
		{'title': 'messages', 'qss': (Message.objects.all(), 'sent_at'), 'pos': 3},
		{'title': 'borrower_comment', 'qss': (BorrowerComment.objects.all(), 'created_at'), 'pos': 4},
		{'title': 'booking_pro', 'qss': (Booking.objects.filter(state__in=[BOOKING_STATE.PROFESSIONAL, BOOKING_STATE.PROFESSIONAL_SAW]), 'created_at', Count('uuid')), 'pos': 5},
		{'title': 'asked_booking', 'qss': (Booking.objects.all(), 'created_at', Count('uuid')), 'pos': 6},
		{'title': 'car_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list).filter(~Q(product__carproduct=None)), 'created_at', Count('uuid')), 'pos': 7},
		{'title': 'sum_total_amount_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Sum('total_amount')), 'pos': 8},
		{'title': 'patrons_private', 'qss': (Patron.objects.filter(Q(is_professional=False) | Q(is_professional=None)) , 'date_joined'), 'pos': 9},
		{'title': 'products_private', 'qss': (Product.objects.filter(owner__is_professional=False), 'created_at'), 'pos': 10},
		{'title': 'other_item_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list).filter(Q(product__realestateproduct=None, product__carproduct=None)), 'created_at', Count('uuid')), 'pos': 11},
		{'title': 'patrons_professionnal', 'qss': (Patron.objects.filter(is_professional=True), 'date_joined'), 'pos': 12},
		{'title': 'products', 'qss': (Product.objects.all(), 'created_at'), 'pos': 13},
		{'title': 'incident_declaration', 'qss': (Booking.objects.filter(state__in=[BOOKING_STATE.INCIDENT]), 'created_at', Count('uuid')), 'pos': 14},
		{'title': 'booking_private', 'qss': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Count('uuid')), 'pos': 15},
		{'title': 'average_total_amount_asked_booking', 'qss': (Booking.objects.all(), 'created_at', Avg('total_amount')), 'pos': 16},
		{'title': 'real_estate_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list).filter(~Q(product__realestateproduct=None)), 'created_at', Count('uuid')), 'pos': 17},
		{'title': 'sum_total_amount_asked_booking', 'qss': (Booking.objects.all(), 'created_at', Sum('total_amount')), 'pos': 18},
		{'title': 'patrons', 'qss': (Patron.objects.all(), 'date_joined'), 'pos': 19},
		{'title': 'need_assurancy_asked_booking', 'qss': (Booking.objects.filter(Q(product__category__need_insurance=True)), 'created_at', Count('uuid')), 'pos': 20},
		{'title': 'other_item_product', 'qss': (Product.objects.filter(carproduct=None).filter(realestateproduct=None), 'created_at'), 'pos': 21},
		{'title': 'car_product', 'qss': (CarProduct.objects.all(), 'created_at'), 'pos': 22},
		{'title': 'real_estate_product', 'qss': (RealEstateProduct.objects.all(), 'created_at'), 'pos': 23},
		{'title': 'average_total_amount_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Avg('total_amount')), 'pos': 24},
		{'title': 'owner_comment', 'qss': (OwnerComment.objects.all(), 'created_at'), 'pos': 25},
		{'title': 'sum_total_amount_car_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list).filter(~Q(product__carproduct=None)), 'created_at', Sum('total_amount')), 'pos': 26},
		{'title': 'sum_total_amount_real_estate_booking', 'qss': (Booking.objects.filter(state__in=booking_transaction_list).filter(~Q(product__realestateproduct=None)), 'created_at', Sum('total_amount')), 'pos': 27},
	]

	new_stat = []

	for qss in qss_list:
		adata = qss.copy()
		adata['qss'] = qsstats.QuerySetStats(*qss['qss']).time_series(datetime.date(year, 1, 1), datetime.date(year, 12, 31), interval='months')
		new_stat.append(adata)

	sorted_list = sorted(new_stat, key=lambda k: k['pos'])

	return render_to_response("reporting/admin/stats.html", {}, RequestContext(request, {'stats': sorted_list}),)



def stats_by_patron(request):
	booking_stats = Patron.objects.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')
	product_stats = Patron.objects.annotate(num_products=Count('products')).order_by('-num_products')

	return render_to_response("reporting/admin/patron_stats.html",
   		{},
   		RequestContext(request, {'booking_stats': booking_stats, 'product_stats': product_stats}),
   	)

def stats_by_patron_detail(request, patron_id):
	patron = get_object_or_404(Patron, pk=patron_id)
	
	booking_stats = patron.products.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')
	category_stats = patron.products.values('category__name', 'category__pk').annotate(num_products=Count('pk'))


	return render_to_response("reporting/admin/patron_stats_detail.html",
   		{},
   		RequestContext(request, {'patron': patron, 'booking_stats': booking_stats, 'category_stats': category_stats}),
   	)

def stats_by_product(request):
	booking_stats = Product.objects.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')

	return render_to_response("reporting/admin/product_stats.html",
   		{},
   		RequestContext(request, {'booking_stats': booking_stats}),
   	)

def stats_by_product_detail(request, product_id):
	product = get_object_or_404(Product, pk=product_id)

	return render_to_response("reporting/admin/product_stats_detail.html",
   		{},
   		RequestContext(request, {'product': product}),
   	)

def stats_by_category(request):
	product_stats = Category.tree.annotate(num_products=Count('products')).order_by('-num_products')
	booking_stats = Category.tree.annotate(num_products_bookings=Count('products__bookings')).order_by('-num_products_bookings')


	return render_to_response("reporting/admin/category_stats.html",
		{},
		RequestContext(request, {'product_stats': product_stats, 'booking_stats': booking_stats})
	)

def stats_by_category_detail(request, category_id):
	category = Category.tree.get(pk=category_id)

	booking_stats = category.products.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')
	patron_stats = category.products.values('owner__username', 'owner__pk').annotate(num_products=Count('pk')).order_by('-num_products')
	owner_stats = category.products.values('owner__username', 'owner__pk').annotate(num_bookings=Count('bookings')).order_by('-num_bookings')

	bookings_count = category.products.aggregate(num_bookings=Count('bookings'))


	return render_to_response("reporting/admin/category_stats_detail.html",
		{},
		RequestContext(request, {'category': category, 'booking_stats': booking_stats, 'bookings_count': bookings_count, 'patron_stats': patron_stats, 'owner_stats': owner_stats })
	)

def stats_by_city(request):
	 patron_stats = Patron.objects.extra(tables=['accounts_address'], where=['"accounts_patron"."default_address_id" = "accounts_address"."id"'], select={'city': 'lower(accounts_address.city)'}).values('city').annotate(Count('id')).order_by('-id__count')
	 product_stats = Product.objects.extra(tables=['accounts_address'], where=['"products_product"."address_id" = "accounts_address"."id"'], select={'city': 'lower(accounts_address.city)'}).values('city').annotate(Count('id')).order_by('-id__count')
	 booking_stats = Booking.objects.extra(select={'city': 'lower(accounts_address.city)'}, tables=["products_product", "accounts_address"], where=['"products_product"."address_id" = "accounts_address"."id"', '"rent_booking"."product_id" = "products_product"."id"']).values('city').annotate(Count('pk')).order_by('-pk__count')
	 booking_amounts_stats = Booking.objects.extra(select={'city': 'lower(accounts_address.city)'}, tables=["products_product", "accounts_address"], where=['"products_product"."address_id" = "accounts_address"."id"', '"rent_booking"."product_id" = "products_product"."id"']).values('city').annotate(Sum('total_amount')).order_by('-total_amount__sum')
	 
	 return render_to_response("reporting/admin/city_stats.html",
   		{},
   		RequestContext(request, {'patron_stats': patron_stats, 'product_stats': product_stats, 'booking_stats': booking_stats, 'booking_amounts_stats': booking_amounts_stats}),
   	)

def stats_by_city_detail(request, city):
	booking_stats = Patron.objects.filter(default_address__city__iexact=city).annotate(num_bookings=Count('bookings')).order_by('-num_bookings')
	product_stats = Patron.objects.filter(default_address__city__iexact=city).annotate(num_products=Count('products')).order_by('-num_products')

	return render_to_response("reporting/admin/city_stats_detail.html",
   		{},
   		RequestContext(request, {'booking_stats': booking_stats, 'product_stats': product_stats, 'city': city}),
   	)



stats = staff_member_required(stats)
stats_by_patron = staff_member_required(stats_by_patron)
stats_by_patron_detail = staff_member_required(stats_by_patron_detail)
stats_by_product = staff_member_required(stats_by_product)
stats_by_product_detail = staff_member_required(stats_by_product_detail)
stats_by_category = staff_member_required(stats_by_category)
stats_by_category_detail = staff_member_required(stats_by_category_detail)
stats_by_city = staff_member_required(stats_by_city)
stats_by_city_detail = staff_member_required(stats_by_city_detail)
