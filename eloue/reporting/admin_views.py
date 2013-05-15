# -*- coding: utf-8 -*-
import datetime
import qsstats

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Avg, Sum, Q, Count

from eloue.accounts.models import Patron
from eloue.products.models import Product, CarProduct, RealEstateProduct, Category
from eloue.rent.models import Booking, OwnerComment, BorrowerComment

from django_messages.models import Message

from django.shortcuts import get_object_or_404



def stats(request):
	query_data = request.GET.copy()

	if query_data.get('year'):
		year = int(query_data.get('year'))
	else:
		year = int(2012)

	data = {}

	booking_transaction_list = [Booking.STATE.PENDING, Booking.STATE.ONGOING, Booking.STATE.ENDED, Booking.STATE.INCIDENT, Booking.STATE.CLOSING, Booking.STATE.CLOSED]

	qss_parameters_list = {
		'patrons': (Patron.objects.all(), 'date_joined'),
		'patrons_private': (Patron.objects.filter(Q(is_professional=False) | Q(is_professional=None)) , 'date_joined'),
		'patrons_professionnal': (Patron.objects.filter(is_professional=True), 'date_joined'),
		'products': (Product.objects.all(), 'created_at'),
		'products_pro': (Product.objects.filter(owner__is_professional=True), 'created_at'),
		'products_private': (Product.objects.filter(owner__is_professional=False), 'created_at'),
		'car_product': (CarProduct.objects.all(), 'created_at'),
		'real_estate_product': (RealEstateProduct.objects.all(), 'created_at'),
		'other_item_product': (Product.objects.filter(carproduct=None).filter(realestateproduct=None), 'created_at'),
		'asked_booking': (Booking.objects.all(), 'created_at', Count('uuid')),
		'booking_pro': (Booking.objects.filter(state__in=[Booking.STATE.PROFESSIONAL, Booking.STATE.PROFESSIONAL_SAW]), 'created_at', Count('uuid')),
		'booking_private': (Booking.objects.filter(state__in=booking_transaction_list), 'created_at', Count('uuid')),
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
		'messages': (Message.objects.all(), 'sent_at'),
		'borrower_comment': (BorrowerComment.objects.all(), 'created_at'),
		'owner_comment': (OwnerComment.objects.all(), 'created_at'),
	}

	for key, value in qss_parameters_list.items():
		data[key] = qsstats.QuerySetStats(*value).time_series(datetime.date(year, 1, 1), datetime.date(year, 12, 31), interval='months')


	return render_to_response(
        "reporting/admin/stats.html",
		{},
		RequestContext(request, {'stats': data}),
    )


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

	 
	 return render_to_response("reporting/admin/city_stats.html",
   		{},
   		RequestContext(request, {'patron_stats': patron_stats, 'product_stats': product_stats, 'booking_stats': booking_stats}),
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
