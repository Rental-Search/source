# coding=utf-8
import re, sys
import xlrd
from django.core.management.base import BaseCommand
from django.core.files import uploadedfile
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing

def next_row(sheet, row):
    return (unicode(sheet.cell(row, i).value) for i in xrange(sheet.ncols))


class Command(BaseCommand):
	#args = "[xls_path, images_folder"]
	help = "Import given xls file for pro user"

	def handle(self, *args, **options):
		from eloue.products.models import Picture, Price, Category, Product, UNIT
		from eloue.products.models import Patron

		try:
			patron = Patron.objects.get(pk=22750)
			address = patron.addresses.all()[0]
		except Patron.DoesNotExist:
			print "Can't find the user"
			return
		if len(args) != 2:
			print "I need exactly two argument"
			return
		with open(args[0]) as xlsx:
			sheet = xlrd.open_workbook(file_contents=xlsx.read()).sheets()[0]
			rows = iter(xrange(sheet.nrows))
			header = tuple(next_row(sheet, next(rows))) # the header line
			next_row(sheet, next(rows)) # the emtpy line
			for row in iter(rows):
				while True:
					try:
						product_row = dict(zip(header, next_row(sheet, row)))
						image_name = product_row["photo"]
						summary = product_row["titre"]
						description = product_row["description"]
						try:
							category = Category.objects.get(slug=product_row["categorie"])
						except:
							print "error category: " + product_row["categorie"]
						
						product = Product.objects.create(
							summary=summary,
							description=description,
							deposit_amount=0,
							category=category,
							address=address,
							owner=patron
						)
						product.prices.add(Price(amount=1, unit=UNIT.DAY))
						
						image_path = '%s/%s' % (args[1], image_name)
						try:
							with closing(open(image_path)) as image:
								picture = Picture.objects.create(image=uploadedfile.SimpleUploadedFile(name='img', content=image.read()))
								product.pictures.add(picture)
						except:
							print "error: " + image_path

						product.save()
						print product
					except:
						break
					else:
						break
