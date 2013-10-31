# coding=utf-8
import xlrd
from django.core.management.base import BaseCommand

def next_row(sheet, row):
    return (unicode(sheet.cell(row, i).value) for i in xrange(sheet.ncols))


class Command(BaseCommand):
	help = "Import given xls file for pro agencies"

	def handle(self, *args, **options):
		from eloue.accounts.models import Patron, ProAgency

		if len(args) != 2:
			print "I need exactly 2 arguments: table path, patron id"
			return
		try:
			patron = Patron.objects.get(pk=args[1])
		except Patron.DoesNotExist:
			print "Can't find the user"
			return

		with open(args[0]) as xlsx:
			sheet = xlrd.open_workbook(file_contents=xlsx.read()).sheets()[0]
			rows = iter(xrange(sheet.nrows))
			header = tuple(next_row(sheet, next(rows))) #the header line

			for row in iter(rows):
				while True:
					try:
						pro_agency_row = dict(zip(header, next_row(sheet, row)))
						pro_agency = ProAgency.objects.create(
							patron=patron,
							name=pro_agency_row["name"],
							address1=pro_agency_row["address1"],
							zipcode=str(int(float(pro_agency_row["zipcode"]))),
							city=pro_agency_row["city"],
							phone_number=pro_agency_row["phone"]
						)
						print pro_agency
					except Exception,e:
						print e
						break
					else:
						break

			