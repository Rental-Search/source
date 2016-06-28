import xlrd
import unicodedata

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from accounts.models import Patron
from accounts.models import PhoneNumber

class Command(BaseCommand):
	help = "import User for euro game 2016"

	isUserExist  = False
	newuser_count = 0
	def handle(self, *args, **options):

		if len(args) > 0:
			# Read file data
			content = xlrd.open_workbook(args[0])
			sh = content.sheet_by_index(0)
			for x in range(1160, sh.nrows):
				firstname = sh.row(x)[2].value
				lastname = sh.row(x)[3].value
				email = sh.row(x)[4].value
				phonenumber =  str(int(sh.row(x)[5].value))
				try:
					zipcode = str(int(sh.row(x)[6].value))
				except Exception, e:
					zipcode = "00000"
					pass
				
				Password = 'JEUEURO2016'

				firstname = firstname.title()
				username = firstname + lastname[0].upper()
				username = username.replace(" ", "")

				# Remove French Accents
				username = unicodedata.normalize('NFKD', username).encode('ASCII', 'ignore')
				
				# Add 0 to phonenumber
				phonenumber = '0' +  phonenumber
				# Check User exist
				try:
					a = Patron.objects.get(email=email)
					self.isUserExist = True
				except Exception, e:
					self.isUserExist = False

				if (self.isUserExist == False):
					try:
						newuser = Patron.objects.create(email=email, username=username, slug=username,
							last_name=lastname, first_name=firstname)
						newuser.set_password(Password)

						newphone = PhoneNumber()
						newphone.id = newuser.id
						newphone.number = phonenumber
						newphone.kind = 2
						newuser.phones.add(newphone)
						newuser.save()
						self.newuser_count += 1
					except Exception, e:
						print e
			print "Total new user added : %d" % self.newuser_count

		else:
			print 'Usage python ./manage.py import_game2016 excelfile'
