# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing
from decimal import Decimal
import re
import unicodedata
import urllib

category_mapping = {
	'categorie.php?catego=1': 'digital-camcorders',
	'categorie.php?catego=2': 'camcorder-accessories',
	'categorie.php?catego=3': 'micro',
	'categorie.php?catego=4': 'connections',
	'categorie.php?catego=5': 'camcorder-accessories',
	'categorie.php?catego=6': 'camcorder-accessories',
	'categorie.php?catego=7': 'accessories-cameras',
	'categorie.php?catego=8': 'connections',
	'categorie.php?catego=9': 'game-of-light',
	'categorie.php?catego=11': 'videoprojector',
	'categorie.php?catego=13': 'camcorder-accessories',
	'categorie.php?catego=14': 'objectives',
	'categorie.php?catego=16': 'game-of-light',
	'categorie.php?catego=19': 'devices',
	'categorie.php?catego=20': 'camcorder-accessories',

}
class Command(BaseCommand):
	help = 'Importation for Trait de lumiere'

	base_url = 'http://www.traitdelumiere-location.com/loc/'

	nb_product = 0

	product_list_tag = {
		"name" : "div",
		"attrs": {
			"class" : "item"
		}
	}

	product_url_tag = {
		"name" : "a",
	}

	summary_tag = {
		"name" : "h1",
	}

	description_tag = {
		"name" : "div",
		"attrs": {
			"class": "produit_texte",
		}
	}

	price_tag = {
		"name" : "div",
		"attrs" : {
			"class": "ajout_panier"
		}
	}

	image_tag = {
		"name" : "img",
		"attrs" : {
			"class": "produitimg"
		}
	}

	def _subpage_crawler(self):
		while True:
			try:
				family = self.product_families.pop()
			except IndexError:
				break

			with closing(urlopen(self.base_url + family)) as product_list_page:
				product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
				product_list = product_list_soup.find_all(self.product_list_tag["name"], self.product_list_tag["attrs"])
				for product in product_list:
					product_url = product.find(self.product_url_tag["name"]).get('href')
					self.product_links[product_url] = family

	def _product_crawler(self):
		from products.models import Product, Picture, Price

		while True:
			try:
				product_url, category = self.product_links.popitem()
			except KeyError:
				break

			try:
				with closing(urlopen(self.base_url + product_url)) as product_page:
					product_soup = BeautifulSoup(product_page, 'html.parser')
			except HTTPError:
				print 'error loading page for object at url', product_url

			# Get description of product
			description = product_soup.find(self.description_tag["name"], self.description_tag["attrs"]).text
			#print 'Description : %s' % description


			# Get price of product
			price = product_soup.find(self.price_tag["name"], self.price_tag["attrs"])
			price = price.find('h4').text
			price = str(float(''.join(x for x in price if x.isdigit())) * 1.2)
			#print 'Price : %s' % price

			# Get summary of product
			summary = product_soup.find('h1').text
			summary = (summary.split("//")[1]).strip()
			#print 'Summary :%s' % summary

			# Get image of product
			image_url = self.base_url + product_soup.find(self.image_tag["name"], self.image_tag["attrs"]).get('src')
			image_url = image_url.replace(' ', '%20')
			image_url = image_url.encode('utf-8')

			redirect_url = self.base_url + product_url

			self.nb_product += 1

			deposit_amount = 0.0

			from products.models import Category, Price
			from products.choices import UNIT

			try:
				
				product = Product.objects.create(
					summary=summary, description=description,
					deposit_amount=deposit_amount, address=self.address, owner=self.patron,
					category=Category.objects.get(slug=category_mapping[category]), is_allowed=False, redirect_url=redirect_url
					)

				try:
					with closing(urlopen(image_url)) as image:
						product.pictures.add(Picture.objects.create(
							image=uploadedfile.SimpleUploadedFile(
								name='img', content=image.read())
							)
						)
				except HTTPError as e:
					print '\nerror loading image for object at url:', image_url

				try:
					product.prices.add(Price(amount=price, unit=UNIT.DAY))
				except Exception, e:
					print 'PRICE ERROR'
					break
			except Exception, e:
				print 'CANNOT CREATE THE PRODUCT %s \n' % (summary)
				print 'error: %s' % str(e)
				break

		print "total product %s" % self.nb_product  

	def handle(self, *args, **options):
		from accounts.models import Patron, Address

	 	self.product_links = {}

	 	# Get the Pro
	 	try:
	 		self.patron = Patron.objects.get(username='traitdelumiere')

	 	except Exception, e:
	 		print "Can't find Trait de lumiere"

	 	# Get the default address
	 	self.address = self.patron.default_address or self.patron.addresses.all()[0]

	 	self.product_families = [
	 		'categorie.php?catego=1',
	 		'categorie.php?catego=2',
	 		'categorie.php?catego=3',
	 		'categorie.php?catego=4',
	 		'categorie.php?catego=5',
	 		'categorie.php?catego=6',
	 		'categorie.php?catego=7',
	 		'categorie.php?catego=8',
	 		'categorie.php?catego=9',
	 		'categorie.php?catego=11',
	 		'categorie.php?catego=13',
	 		'categorie.php?catego=14',
	 		'categorie.php?catego=16',
	 		'categorie.php?catego=19',
	 		'categorie.php?catego=20',
	 	]

	 	self._subpage_crawler()
	 	self._product_crawler()