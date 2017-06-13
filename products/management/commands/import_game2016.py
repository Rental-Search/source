import xlrd
import unicodedata

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from accounts.models import Patron
from accounts.models import PhoneNumber
from urllib2 import urlopen
import tempfile
from django.template.defaultfilters import slugify


class Command(BaseCommand):
	help = "import User for euro game 2016"

	isUserExist  = False
	newuser_count = 0
	usernameExist_count = 0
	userlist = set()

	def handle(self, *args, **options):

		# Read file data
		f = urlopen("http://eloue.s3.amazonaws.com/base_jeuconcourseuro_20160622.xls")
		content = xlrd.open_workbook(file_contents=f.read())
		f.close()
		sh = content.sheet_by_index(0)

		for x in range(1, sh.nrows):
			firstname = sh.row(x)[2].value
			lastname = sh.row(x)[3].value
			email = sh.row(x)[4].value
			try:
				phonenumber =  str(int(sh.row(x)[5].value))
			except Exception, e:
				phonenumber = None

			Password = 'JEUEURO2016'

			firstname = firstname.title()
			username = firstname + lastname[0].upper()
			username = username.replace(" ", "")

			# Remove French Accents
			username = unicodedata.normalize('NFKD', username).encode('ASCII', 'ignore')
			
			#print username
			# Add 0 to phonenumber
			if phonenumber:
				phonenumber = '0' +  phonenumber
			
			# Check User exist
			patron_count = Patron.objects.filter(email=email).count()

			if patron_count == 0:

				#Check if the username exist
				patrons = Patron.objects.filter(username__startswith=username)
				if patrons.count() > 0:
					username = username + "%s" % patrons.count()

				#Check if the slug exist
				slug=slugify(username)
				patrons = Patron.objects.filter(slug__startswith=slug)
				if patrons.count() > 0:
					slug = slug + "%s" % patrons.count()

				try:
					newuser = Patron.objects.create(email=email, username=username, slug=slug,
						last_name=lastname, first_name=firstname)
					newuser.set_password(Password)

					# Add phone number
					if phonenumber:
						newuser.phones.add(PhoneNumber(number=phonenumber))
					
					newuser.save()
					self.newuser_count += 1
					print newuser.email
				except Exception, e:
					print e
					pass

		print "Total new user added : %d" % self.newuser_count


