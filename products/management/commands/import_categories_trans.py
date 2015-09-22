import xlrd
import urllib2

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from products.models import Category

def next_row(sheet, row):
    return (unicode(sheet.cell(row, i).value) for i in xrange(sheet.ncols))


class Command(BaseCommand):
	help = "Import translation of categories name"

	def handle(self, *args, **options):

		try:
			xlsx = urllib2.urlopen("http://eloue.s3.amazonaws.com/categories.xls")
		except:
			print "Impossible to download the file"

		sheet = xlrd.open_workbook(file_contents=xlsx.read()).sheets()[0]
		rows = iter(xrange(sheet.nrows))
		header = tuple(next_row(sheet, next(rows)))

		for row in iter(rows):
			while True:
				try:
					category_row = dict(zip(header, next_row(sheet, row)))
					category = Category.objects.get(pk=int(float(category_row['id'])))
					category.name_da = category_row['name_da']
					category.save()
				except Exception,e:
					print e
					break
				else:
					break