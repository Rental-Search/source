# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing
from decimal import Decimal
import re
import urllib
import threading

category_mapping = {
	'11-ecrans-lcd-informatique': 'led',
	'171-imprimantes-laser': 'imprimante-laser-couleur',
	'44-inferieur-a-2500-lumens': 'videoprojecteur',
	'45-de-2500-a-3500-lumens': 'videoprojecteur',
	'46-de-5000-a-10-000-lumens': 'videoprojecteur',
	'47-plus-de-10-000-lumens': 'videoprojecteur',
	'166-de-3500-a-5000-lumens': 'videoprojecteur',
	'164-courte-focale': 'videoprojecteur',
	'49-enceinte-active': 'enceintes-salon',
	'50-enceintes': 'enceintes-salon',
	'51-amplificateurs': 'amplificateur',
	'52-consoles-de-mixages': 'effets-son',
	'54-micro-sans-fils-hf': 'micro-sans-fil',
	'55-micro-cravate-et-serre-tete': 'micro-sans-fil',
	'56-micro-a-fils': 'micro-filaire',
	'170-micro-de-reportage': 'micro-filaire', 
	'57-lecteur-cd-et-dat': 'lecteur-cd-de-salon',
	'175-micro-col-de-cygne': 'micro-filaire',
	'60-lecteurenregistreur-audio': 'micro-sans-fil',
	'62-audio-conference': 'micro-sans-fil',
	'64-pieds-micro': 'micro-filaire',
	'67-led': 'led',
	'68-lcd': 'tv-lcd',
	'69-plasma': 'plasma',
	'72-pieds-totem-pour-ecrans-plats': 'tv-lcd',
	'22-systeme-de-vote-interactif': 'accessoires-tv',
	'73-magnetoscopes': 'lecteur-enregistreur-vhs',
	'172-camescopes-hdv': 'camescopes-numeriques',
	'174-camescopes-a-disque-dur': 'camescopes-numeriques',
	'173-camescopes-dv': 'camescopes-numeriques',
	'76-lecteur-enregistreur-video': 'lecteur-dvd',
	'16-lecteurs-dvd-blu-ray': 'lecteur-enregistreur-blu-ray',
	'168-moniteurs-de-controle': 'accessoires-camescope',
	'83-sur-pieds-et-trepieds': 'videoprojecteur',
	'84-sur-cadre-aluminium-pliable': 'videoprojecteur',
	'85-ecrans-toiles-retro': 'videoprojecteur',
	'87-mac-portables': 'mac-portable',
	'88-pc-portables': 'pc-portable',
	'89-ecrans-lcd-led': 'tv-lcd',
	'92-pointer-de-presentation': 'micro-sans-fil',
	'94-distributeurs-informatique': 'accessoires-camescope',
	'95-selecteurs-de-sources': 'connectique',
	'169-moniteurs-informatique': 'tv-lcd',
	'97-switcher-de-presentation': 'switch',
	'177-lia': 'videoprojecteur',
	'100-par-5664': 'projecteur-diapo',
	'101-led': 'led',
	'102-pc': 'jeu-de-lumiere',
	'103-decoupes': 'jeu-de-lumiere',
	'104-poursuites': 'jeu-de-lumiere',
	'105-lyres': 'jeu-de-lumiere',
	'107-console-d-eclairage-': 'jeu-de-lumiere',
	'109-bloc-de-puissance': 'blocs-de-puissance',
	'112-pupitres': 'decoration',
	'113-scenes': 'decoration',
}
class Command(BaseCommand):
	help = 'Importation for dvttoulouse'

	base_url = 'http://www.dvt.fr/'

	nb_product = 0

	thread_num = 1

	product_list_tag = {
		"name" : "div",
		"attrs": {
			"class" : "ajax_block_product"
		}
	}

	product_url_tag = {
		"name" : "a",
	}

	summary_tag = {
		"name" : "h1",
		"attrs": {
			"class": "title_detailproduct",
		}
	}

	description_tag = {
		"name" : "div",
		"attrs": {
			"id": "more_info_sheets",
		},
		"second_attrs":{
			"id": "idTab1",
		}
	}

	price_tag = {
		"name" : "span",
		"attrs" : {
			"id": "our_price_display"
		}
	}

	image_tag = {
		"name" : "img",
		"attrs" : {
			"id": "bigpic"
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
				with closing(urlopen(product_url)) as product_page:
					product_soup = BeautifulSoup(product_page, 'html.parser')
			except HTTPError:
				print 'error loading page for object at url', product_url

				#print product_soup
			# Get description of product
			try:
				description = (product_soup.find(self.description_tag["name"], self.description_tag["attrs"])).find(self.description_tag["name"], self.description_tag["second_attrs"]).text
				description = description.encode('latin-1')
			except Exception, e:
				description = ' '

			

			# # Get price of product
			try:
				price = product_soup.find(self.price_tag["name"], self.price_tag["attrs"]).text
				price = re.findall('\d+', price)
				price = (price[0].strip().replace(u'€', '').replace(',', '.').replace(' ', '').replace(':', ''))
				price = int(price)
			except Exception, e:
				price = None

			deposit_amount = 650.0
			if price > 250:
				deposit_amount = 1200.0
			price = str(price)
			# # Get summary of product
			try:
				summary = product_soup.find(self.summary_tag["name"], self.summary_tag["attrs"]).text
			except Exception, e:
				summary = ' '


			# # Get image of product
			try:
				image_url = product_soup.find(self.image_tag["name"], self.image_tag["attrs"]).get('src')
			except Exception, e:
				image_url = None
			

			redirect_url = product_url

			# self.nb_product += 1

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

		# print "total product %s" % self.nb_product  

	def handle(self, *args, **options):
		from accounts.models import Patron, Address

	 	self.product_links = {}

	 	# Get the Pro
	 	try:
	 		self.patron = Patron.objects.get(slug='dvttoulouse')

	 	except Exception, e:
	 		print "Can't find Trait de lumiere"

	 	# Get the default address
	 	self.address = self.patron.default_address or self.patron.addresses.all()[0]

	 	self.product_families = [
	 		'11-ecrans-lcd-informatique',
	 		'171-imprimantes-laser',
	 		'44-inferieur-a-2500-lumens',
			'45-de-2500-a-3500-lumens',
			'46-de-5000-a-10-000-lumens',
			'47-plus-de-10-000-lumens',
			'166-de-3500-a-5000-lumens',
			'164-courte-focale',
			'49-enceinte-active',
			'50-enceintes',
			'51-amplificateurs',
			'52-consoles-de-mixages',
			'54-micro-sans-fils-hf',
			'55-micro-cravate-et-serre-tete',
			'56-micro-a-fils',
			'170-micro-de-reportage',
			'57-lecteur-cd-et-dat',
			'175-micro-col-de-cygne',
			'60-lecteurenregistreur-audio',
			'62-audio-conference',
			'64-pieds-micro',
			'67-led',
			'68-lcd',
			'69-plasma',
			'72-pieds-totem-pour-ecrans-plats',
			'22-systeme-de-vote-interactif',
			'73-magnetoscopes',
			'172-camescopes-hdv',
			'174-camescopes-a-disque-dur',
			'173-camescopes-dv',
			'76-lecteur-enregistreur-video',
			'16-lecteurs-dvd-blu-ray',
			'168-moniteurs-de-controle',
			'83-sur-pieds-et-trepieds',
			'84-sur-cadre-aluminium-pliable',
			'85-ecrans-toiles-retro',
			'87-mac-portables',
			'88-pc-portables',
			'89-ecrans-lcd-led',
			'92-pointer-de-presentation',
			'94-distributeurs-informatique',
			'95-selecteurs-de-sources',
			'169-moniteurs-informatique',
			'97-switcher-de-presentation',
			'177-lia',
			'100-par-5664',
			'101-led',
			'102-pc',
			'103-decoupes',
			'104-poursuites',
			'105-lyres',
			'107-console-d-eclairage-',
			'109-bloc-de-puissance',
			'112-pupitres',
			'113-scenes',
	 	]

	 	# self._subpage_crawler()
	 	# self._product_crawler()

	 	for i in xrange(self.thread_num):
	 		threading.Thread(target=self._subpage_crawler).start()
	 	for thread in threading.enumerate():
	 		if thread is not threading.currentThread():
	 			thread.join()

		# Create the products in the database
		for i in xrange(self.thread_num):
			threading.Thread(target=self._product_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()