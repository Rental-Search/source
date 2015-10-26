# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
import sendgrid, time
from accounts.models import Patron



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

		patron1 = Patron.objects.filter(email="hugo.woog@gmail.com")
		emails = [patron.email for patron in patron1]

		notifications = [
			{"recipient": emails, "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"},
			{"recipient": ["hugo.woog@e-loue.com"], "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"}
		]

		for notification in notifications:
			self._send_notification(notification)
			time.sleep(5)

		# while notification in notifications:
		# 	self._send_notification(notification)
		# 	time.sleep(5)




		