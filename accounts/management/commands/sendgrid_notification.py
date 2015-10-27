# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
import sendgrid, time, datetime
from datetime import timedelta
from accounts.models import Patron
from rent.models import Booking, BookingLog
from products.models import Product
from rent.choices import BOOKING_STATE



class Command(BaseCommand):
	help = 'Send notification to our users'


	def _send_notification(self, notification):

		# MAKE A SECURE CONNECTION TO SENDGRID
		# Fill in the variables below with your SendGrid 
		# username and password.
		#========================================================#
		sg_username = "hugow"
		sg_password = "Hl131193"


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
				# patrons = Patron.... requette ORM Django  

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
		#========================================================#
		status, msg = sg.send(message)

		print msg


	def handle(self, *args, **options):

		date = datetime.datetime.now()

		bookings_ended = Booking.objects.filter(ended_at__day=date.day, ended_at__month=date.month, ended_at__year=date.year, state=BOOKING_STATE.ENDED)
		bookings_rejected = Booking.objects.filter(ended_at__day=date.day, ended_at__month=date.month, ended_at__year=date.year, state=BOOKING_STATE.REJECTED)
		bookings_outdated = Booking.objects.filter(started_at__day=date.day, started_at__month=date.month, started_at__year=date.year, state=BOOKING_STATE.OUTDATED)
		bookings_canceled = BookingLog.objects.filter(created_at__day=date.day, created_at__month=date.month, created_at__year=date.year, target_state=BOOKING_STATE.CANCELED)

		products_complete = Product.objects.filter(pictures__isnull=False).exclude(description="")
		products_miss_pic = Product.objects.filter(pictures__isnull=True).exclude(description="")
		products_miss_desc = Product.objects.filter(description="", pictures__isnull=False)
		products_empty = Product.objects.filter(description="", pictures__isnull=True)


		notifications = [
			{"recipient": [borrower.email for borrower in Patron.objects.filter(rentals=bookings_ended, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [borrower.email for borrower in Patron.objects.filter(rentals=bookings_ended, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [borrower.email for borrower in Patron.objects.filter(rentals=bookings_ended, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [borrower.email for borrower in Patron.objects.filter(rentals=bookings_ended, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},

			{"recipient": [product.owner.email for product in Patron.objects.filter(products=products_complete, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [product.owner.email for product in Patron.objects.filter(products=products_miss_pic, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [product.owner.email for product in Patron.objects.filter(products=products_miss_desc, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [product.owner.email for product in Patron.objects.filter(products=products_empty, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},

			{"recipient": [patron.email for patron in Patron.objects.filter(rentals__isnull=True, products__isnull=True, date_joined__gte=datetime.date.today() - timedelta(days=1))], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"}
		]

		for notification in notifications:
			# self._send_notification(notification)
			print "bi1 ouej"
			time.sleep(5)



		