# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
import sendgrid, time, datetime
from datetime import timedelta
from accounts.models import Patron
from rent.models import Booking, BookingLog
from products.models import Product
from rent.choices import BOOKING_STATE
from django.db.models import Count



class Command(BaseCommand):
	help = 'Send notification to our users'


	def _send_notification(self, notification):

		# MAKE A SECURE CONNECTION TO SENDGRID
		# Fill in the variables below with your SendGrid 
		# username and password.
		#========================================================#
		sg_username = "benoit.woj@e-loue.com"
		sg_password = "mWv49fVx"


		# CREATE THE SENDGRID MAIL OBJECT
		#========================================================#
		sg = sendgrid.SendGridClient(sg_username, sg_password)
		message = sendgrid.Mail()


		# ENTER THE EMAIL INFORMATION
		#========================================================#
		message.set_from("contact@e-loue.com")
		message.set_subject(" ")
		message.set_text(" ")
		message.set_html(" ")



		# SMTP API
		#========================================================#
		# Add the recipients

		message.smtpapi.set_tos(
			notification["recipient"]
		)

		# App Filters
		filters = {
		    "templates": {
		        "settings": {
		            "enable": "1",
		            "template_id": notification["template_id"]
		        }
		    }
		}
		for app, contents in filters.iteritems():
		    for setting, value in contents['settings'].iteritems():
		        message.add_filter(app, setting, value)


		# SEND THE MESSAGE
		#========================================================
		return sg.send(message)



	def handle(self, *args, **options):

		today = datetime.datetime.now()
		d2 = today - timedelta(days=2)
		d3 = today - timedelta(days=3)
		d5 = today - timedelta(days=5)

		bookings_ended = Booking.objects.filter(ended_at__day=d5.day, ended_at__month=d5.month, ended_at__year=d5.year, state=BOOKING_STATE.ENDED).annotate(borrower_rentals_count=Count('borrower__rentals')).filter(borrower_rentals_count=1).values('borrower__email')
		bookings_rejected = Booking.objects.filter(ended_at__day=d2.day, ended_at__month=d2.month, ended_at__year=d2.year, state=BOOKING_STATE.REJECTED).annotate(borrower_rentals_count=Count('borrower__rentals')).filter(borrower_rentals_count=1).values('borrower__email')
		bookings_outdated = Booking.objects.filter(started_at__day=d2.day, started_at__month=d2.month, started_at__year=d2.year, state=BOOKING_STATE.OUTDATED).annotate(borrower_rentals_count=Count('borrower__rentals')).filter(borrower_rentals_count=1).values('borrower__email')
		bookings_canceled = BookingLog.objects.filter(created_at__day=d2.day, created_at__month=d2.month, created_at__year=d2.year, target_state=BOOKING_STATE.CANCELED).annotate(borrower_rentals_count=Count('booking__borrower__rentals')).filter(borrower_rentals_count=1).values('booking__borrower__email')
		
		products_complete = Product.objects.filter(pictures__isnull=False, created_at__day=d5.day, created_at__month=d5.month, created_at__year=d5.year).exclude(description="").annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		products_miss_pic = Product.objects.filter(pictures__isnull=True, created_at__day=d3.day, created_at__month=d3.month, created_at__year=d3.year).exclude(description="").annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		products_miss_desc = Product.objects.filter(description="", pictures__isnull=False, created_at__day=d3.day, created_at__month=d3.month, created_at__year=d3.year).annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		products_empty = Product.objects.filter(description="", pictures__isnull=True, created_at__day=d3.day, created_at__month=d3.month, created_at__year=d3.year).annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		
		patron_inactives = Patron.objects.filter(rentals__isnull=True, products__isnull=True, date_joined__day=d5.day, date_joined__month=d5.day, date_joined__year=d5.year)


		notifications = [
			{"name": "loc1", "recipient": [booking['borrower__email'] for booking in bookings_ended], "template_id": "02bfa8c5-db75-4e36-84ac-56e957f3792a"},
			{"name": "locdr1_rejected", "recipient": [booking['borrower__email'] for booking in bookings_rejected], "template_id": "3ee35da2-d85a-439e-b69e-a6e51861f634"},
			{"name": "locdr1_outdated", "recipient": [booking['borrower__email'] for booking in bookings_outdated], "template_id": "3ee35da2-d85a-439e-b69e-a6e51861f634"},
			{"name": "loca1", "recipient": [booking['borrower__email'] for booking in bookings_canceled], "template_id": "98b4f200-209a-4053-b30e-c7a4d5bd5d87"},

			{"name": "prop1", "recipient": [product['owner__email'] for product in products_complete], "template_id": "28faa11f-cd33-403e-a47f-9abb8dfaebb5"},
			{"name": "proppd1", "recipient": [product['owner__email'] for product in products_empty], "template_id": "1b026ada-fc64-41d4-8a8d-e3e2e55b9a7f"},
			{"name": "propd1", "recipient": [product['owner__email'] for product in products_miss_desc], "template_id": "db6f7b78-fd0b-4614-8852-f56ccd305803"},
			{"name": "propp1", "recipient": [product['owner__email'] for product in products_miss_pic], "template_id": "1648216c-b81c-4a69-95a4-2f4f97bdf2fd"},

			{"name": "ina1", "recipient": [patron.email for patron in patron_inactives], "template_id": "eaa65d7d-9908-4d44-9f80-6ccd6d0c90d6"}
		]



		while len(notifications) > 0:
			try:
				notification = notifications.pop()
				status, msg = self._send_notification(notification)
			except:
				print "error"

			print "%s : %s : %s" % (notification["name"], status, msg)



