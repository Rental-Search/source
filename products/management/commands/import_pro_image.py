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
		from products.models import Picture, Price, Category, Product
		from products.choices import UNIT
		from accounts.models import Patron
		if len(args) != 3:
			print "I need exactly three argument table path, image folder path and patron id"
			return
		try:
			patron = Patron.objects.get(pk=args[2])
			address = patron.addresses.all()[0]
		except Patron.DoesNotExist:
			print "Can't find the user"
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
						
						summary = product_row["titre"].lower()
						description = product_row["description"]

						try:
							category = Category.objects.get(slug=product_row["categorie"])
						except:
							print "error category: " + product_row["categorie"]


						try:
							deposit_amount = product_row['caution']
						except:
							deposit_amount = 0
						
						product = Product.objects.create(
							summary=summary,
							description=description,
							deposit_amount=deposit_amount,
							category=category,
							address=address,
							owner=patron
						)
						
						try:
							product.prices.add(Price(amount=product_row['prix_jour'], unit=UNIT.DAY))
						except:
							pass

						try:
							product.prices.add(Price(amount=product_row['prix_weekend'], unit=UNIT.WEEK_END))
						except:
							pass

						try:
							product.prices.add(Price(amount=product_row['prix_semaine'], unit=UNIT.WEEK))
						except:
							pass

						try:
							product.prices.add(Price(amount=product_row['prix_2semaines'], unit=UNIT.TWO_WEEKS))
						except:
							pass

						try:
							product.prices.add(Price(amount=product_row['prix_mois'], unit=UNIT.MONTH))
						except:
							pass
						

						try:
							image_name = product_row["photo"]
						except:
							pass
							
						try:
							image_path = '%s/%s' % (args[1], image_name)
							with closing(open(image_path)) as image:
								picture = Picture.objects.create(image=uploadedfile.SimpleUploadedFile(name='img', content=image.read()))
								product.pictures.add(picture)
						except:
							print image_path
							pass


						try:
							image_url = product_row["photo_url"]
						except:
							pass

						try:
							with closing(urlopen(image_url)) as image:
								picture = Picture.objects.create(image=uploadedfile.SimpleUploadedFile(name='img', content=image.read()))
								product.pictures.add(picture)
						except:
							pass

						product.save()
						print product
					except Exception,e:
						print e
						break
					else:
						break
