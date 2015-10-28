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
			
		#print msg



	def handle(self, *args, **options):

		date = datetime.datetime.now()

		bookings_ended = Booking.objects.filter(ended_at__day=date.day, ended_at__month=date.month, ended_at__year=date.year, state=BOOKING_STATE.ENDED).annotate(borrower_rentals_count=Count('borrower__rentals')).filter(borrower_rentals_count=1).values('borrower__email')
		bookings_rejected = Booking.objects.filter(ended_at__day=date.day, ended_at__month=date.month, ended_at__year=date.year, state=BOOKING_STATE.REJECTED).annotate(borrower_rentals_count=Count('borrower__rentals')).filter(borrower_rentals_count=1).values('borrower__email')
		bookings_outdated = Booking.objects.filter(started_at__day=date.day, started_at__month=date.month, started_at__year=date.year, state=BOOKING_STATE.OUTDATED).annotate(borrower_rentals_count=Count('borrower__rentals')).filter(borrower_rentals_count=1).values('borrower__email')
		bookings_canceled = BookingLog.objects.filter(created_at__day=date.day, created_at__month=date.month, created_at__year=date.year, target_state=BOOKING_STATE.CANCELED).annotate(borrower_rentals_count=Count('booking__borrower__rentals')).filter(borrower_rentals_count=1).values('booking__borrower__email')
		
		products_complete = Product.objects.filter(pictures__isnull=False, created_at__day=date.day, created_at__month=date.month, created_at__year=date.year).exclude(description="").annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		products_miss_pic = Product.objects.filter(pictures__isnull=True, created_at__day=date.day, created_at__month=date.month, created_at__year=date.year).exclude(description="").annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		products_miss_desc = Product.objects.filter(description="", pictures__isnull=False, created_at__day=date.day, created_at__month=date.month, created_at__year=date.year).annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		products_empty = Product.objects.filter(description="", pictures__isnull=True, created_at__day=date.day, created_at__month=date.month, created_at__year=date.year).annotate(owner_products_count=Count('owner__products')).filter(owner_products_count=1).values('owner__email')
		
		patron_inactives = Patron.objects.filter(rentals__isnull=True, products__isnull=True, date_joined__gte=datetime.date.today() - timedelta(days=1))

		notifications = [
			{"recipient": [booking['borrower__email'] for booking in bookings_ended], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [booking['borrower__email'] for booking in bookings_rejected], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [booking['borrower__email'] for booking in bookings_outdated], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [booking['booking__borrower__email'] for booking in bookings_canceled], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},

			{"recipient": [product['owner__email'] for product in products_complete],"template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [product['owner__email'] for product in products_miss_pic],"template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [product['owner__email'] for product in products_miss_desc],"template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": [product['owner__email'] for product in products_empty],"template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},

			{"recipient": [patron.email for patron in patron_inactives], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"}
		]

		for notification in notifications:
			#self._send_notification(notification)
			print notification
			time.sleep(0.5)




		# notifications = [
		# 	{"recipient": "hugo.woog@gmail.com", "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
		# 	{"recipient": "hugo.woog@e-loue.com", "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"}
		# ]

		# while True:
		# 	try:
		# 		recipient = recipients.pop()
		# 	except:
		# 		return False

		# 	status, msg = self._send_notification(recipient)

		# 	if status == 200:
		# 		return True
		# 	else:
		# 		print "error %s" % msg 



	#FOR LATER

	# notifications = [
	# 		(bookings_ended, 'borrower_email'),
	# 		(bookings_ended, 'borrower_email'),
	# 		(bookings_ended, 'borrower_email')
	# 	]

	# 	for notification in notifications:
	# 		[element[notification[1]] for element in notification[0]]	
		

	# 	[element[notification[1]] for element in notification[0]]
	# 	[element['borrower_email'] for element in Booking.objects.filter(ended_at__day=date.day, ended_at__month=date.month, ended_at__year=date.year, state=BOOKING_STATE.ENDED)]
		



		