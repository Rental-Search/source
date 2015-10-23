# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
import sendgrid
from accounts.models import Patron



class Command(BaseCommand):
	help = 'Send notification to ours users'

	def handle(self, *args, **options):

		# notifications =  [
		# 	{"recipient": Patron.objects.all(), "template": "3432342"},
		# 	{"recipient": Patron.objects.all(), "template": "3432342"},
		# 	{"recipient": Patron.objects.all(), "template": "3432342"},
		# 	{"recipient": Patron.objects.all(), "template": "3432342"},
		# ]

		# for notification in notifications:
		# 	send_notication(notification)

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
		message.set_text("Bonjour %firstname,%")
		message.set_html("<h3 style=\"text-indent: 19px; font-family: Helvetica; font-size: 13px; color: #606060;\">Bonjour %firstname%,</h3>")



		# SMTP API
		#========================================================#
		# Add the recipients
				# patrons = Patron.... requette ORM Django  

		message.smtpapi.set_tos([
			"hugo.woog@gmail.com",
			"benoit.woj@e-loue.com"
		])#[patron.email for patron in notification.recipient])

		# Substitutions
		subs = {
		    "%firstname%": [
		        "Hugéé Woàág",
		        "Benoit",
		    ]
		}
		for tag, values in subs.iteritems():
		    for value in values:
		        message.add_substitution(tag, value)

		# App Filters
		filters = {
		    "templates": {
		        "settings": {
		            "enable": "1",
		            "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"     #notification.template
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