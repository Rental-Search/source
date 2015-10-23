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

		# send_notification()

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
		message.set_subject("Mail test for %name%")
		message.set_text("%salutation%")
		message.set_html("<h2>%salutation%</h2>")



		# ADD THE ATTACHMENT
		# The first parameter is the name of the file, 
		# and the second parameter is the path to the file.
		# For the purposes of this demo, the file itself is
		# in the same directory as this Python script
		#========================================================#
		# message.add_attachment("sendgrid_logo.jpg", "sendgrid_logo.jpg")



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
		    "%salutation%": [
		        "%male_greeting%",
		        "%male_greeting%"
		    ],
		    "%name%": [
		        "Hugo Woog",
		        "Benoit Woj"
		    ]
		}
		for tag, values in subs.iteritems():
		    for value in values:
		        message.add_substitution(tag, value)

		# Categories
		categories = [
		    "New users"
		]
		for category in categories:
		    message.add_category(category)

		# Sections
		sections = {
		    "%male_greeting%": "Hello Mr %name%"
		}
		for tag, value in sections.iteritems():
		    message.add_section(tag, value)    

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