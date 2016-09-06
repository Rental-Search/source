import xlrd
import unicodedata

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from accounts.models import Patron
from accounts.models import PhoneNumber
from urllib2 import urlopen
import tempfile
from products.models import ProAgency

class Command(BaseCommand):
	help = "import ProAgency for InterSport"

	def handle(self, *args, **options):

		nb_proagency = 0
		# Read file data
		f = urlopen("http://eloue.s3.amazonaws.com/intersport_agencies2.xlsx")
		content = xlrd.open_workbook(file_contents=f.read())
		f.close()
		sh = content.sheet_by_index(0)

		# Intersport id : 122559
		patron_id=122559

		for x in range(14, sh.nrows):
			name = sh.row(x)[0].value
			address = sh.row(x)[2].value
			try:
				zipcode = str(int(sh.row(x)[3].value))
			except Exception, e:
				zipcode = sh.row(x)[3].value
				pass

			try:
				city = str(sh.row(x)[4].value)
			except Exception, e:
				city = sh.row(x)[4].value
				pass
			
			try:
				phone_number = str(int(sh.row(x)[5].value))
				phone_number = '0' + phone_number
			except Exception, e:
				pass
			
			try:
				newAgency = ProAgency.objects.create(name=name, address1=address, city=city, zipcode=zipcode, phone_number=phone_number, patron_id=patron_id)
				nb_proagency += 1
			except Exception, e:
				raise e

		print 'Total proagency added : %s' % str(nb_proagency)
			# print 'Name: %s' % name
			# print 'address: %s' % address
			# print 'city: %s' % city
			# print 'Zipcode: %s' % zipcode
			# print 'Phone_number: %s' % phone_number
