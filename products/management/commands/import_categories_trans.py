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
			xlsx = urllib2.urlopen(args[0])
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
					if not category.name_da == category_row['name_da']:
						category.name_da = category_row['name_da']
						slug_da = slugify(category.name_da)
						category.slug_da=slug_da

						#Detect if the slug is unique or not...
						if Category.objects.filter(slug_da=slug_da).exists():
							try:
								number = int(slug_da.split("-")[-1])
								category.slug_da = "%s-%s" % (slug_da, number+1)
							except:
								category.slug_da = "%s-1" % (slug_da)
						else:
							category.slug_da=slug_da

						category.save()

				except Exception,e:
					print e
					break
				else:
					break