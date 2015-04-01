# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from django.utils.html import smart_urlquote

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
	'/brh-brise-roche-hydraulique/': 'marteau-piqueur',
	'/cisaille-a-beton/': 'travaux',
	'/cisaille-a-ferraille/' : 'travaux',
	'/combi-pour-arden-20t/' : 'travaux',
	'/decolleuse-pour-800-kg/': 'decolleuse',
	'/pince-de-tri/':'travaux',
	'/mesure-et-signalisation/': 'constructions-modulaires',
	'/modulaires/':'constructions-modulaires',
	'/sanitaires/':'constructions-modulaires',
	'/echafaudages/':'echafaudage',
	'/nacelles-et-camion-nacelles/':'echafaudage',
	'/chariot-elevateur/':'echafaudage',
	'/telescopique/':'echafaudage',
	'/cylindre/':'epandeur-rouleau',
	'/patin-vibrant-pilloneuse-plaque-vibrante/':'travaux',
	'/pied-de-mouton/':'epandeur-rouleau',
	'/chargeuse-articulee/':'travaux',
	'/dumper/':'travaux',
	'/mini-chargeur/':'pelle-pioche-et-tariere',
	'/mini-pelle/':'pelle-pioche-et-tariere',
	'/chauffage-a-air-pulse/':'chauffage',
	'/compresseurs/':'compresseur',
	'/deshumidificateur/':'deshumificateur',
	'/groupes-electrogenes/':'groupe-electrogene',
	'/camion-refrigere/':'remorque-utilitaire',
	'/remorque-tribune/':'remorque-utilitaire',
	'/structures-gonflables/':'jeux-gonflables',
	'/vehicule-prestige/':'berline',
	'/coupe-et-poncage/':'travaux',
	'/espaces-verts/':'travaux',
	'/nettoyage-et-decoration/':'travaux',
	'/traitement-du-beton/':'travaux',
	'/pelleteuses/':'pelle-pioche-et-tariere',
	'/outils-de-demolition-materiel-a-la-vente/':'travaux',
	'/camions-bennes-3t5/':'remorque-utilitaire',
	'/remorques-tp/':'remorque-utilitaire'
}


class Command(BaseCommand):
	args = ''
	help = "Imports given xls file for user 'DEGUIZLAND'"
	
	base_url = 'http://www.axxlocations.fr/cat-produits'

	def _subpage_crawler(self):
		"""Create the list of products by finding the link of each product page"""
		while True:
			try:
				family = self.product_families.pop()
			except IndexError:
				break

			with closing(urlopen(self.base_url + family)) as product_list_page:
				product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
				product_list = product_list_soup.find('ul', class_='list-produits').find_all('li')
				for product in product_list:
					product_url = product.find('a').get('href')
					self.product_links[product_url] = family
  
	def _product_crawler(self):
		from products.models import Product, Picture, Price

		# Return the price in the right format
		def _to_decimal(s):
			from decimal import Decimal as D
			return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))   

		while True:
			try:
				product_url, category = self.product_links.popitem()
			except KeyError:
				break
			try:
				with closing(urlopen(product_url)) as product_page:
					product_soup = BeautifulSoup(product_page, 'html.parser')
			except HTTPError:
				print 'error loading page for object at url', self.base_url + product_url

			# Get the image
			if product_soup.find('img', class_='alignleft wp-post-image'):
				image_url = product_soup.find('img', class_='alignleft wp-post-image').get('src')
			elif product_soup.find('a', class_='lightbox'):
				image_url = product_soup.find('a', class_='lightbox').get('href')
			else:
				image_url = 'http://www.axxlocations.fr/wp-content/themes/axxlocations/img/logo.jpg'

			image_url = smart_urlquote(image_url)

			# Get the title
			infosProduits = product_soup.find('article', class_=re.compile('post[0-9]*')).find('h1').text

			# Get the description
			try: 
				description = product_soup.find('div', id='produit-avantages').text
			except:
				description = ''
				pass

			try:
				description += product_soup.find('div', id='produits-carateristiques').text
			except:
				pass

			# Format the title
			summary = infosProduits

			deposit_amount = 0.0

			# print 'url:%s \n img:%s \n infos:%s \n description:%s \n summary:%s' % (product_url, image_url, infosProduits, description, summary)

			# Create the product
			from products.models import Category, Price
			from products.choices import UNIT

			try:
				product = Product.objects.create(
				summary=summary, description=description, 
				deposit_amount=deposit_amount, address=self.address, owner=self.patron,
				category=Category.objects.get(slug=category_mapping[category]))
				try:
					with closing(urlopen(image_url)) as image:
						product.pictures.add(Picture.objects.create(
							image=uploadedfile.SimpleUploadedFile(
								name='img', content=image.read())
						)
					)
				except HTTPError as e:
					print '\nerror loading image for object at url:', self.base_url + product_url
					pass
			except:
				print 'CANNOT CREATE PRODUCT : %s' % summary
				pass


	def handle(self, *args, **options):
		if len(args) > 1:
			print '2 arguments given, expected one ...'
			return
		try:
			thread_num = int(args[0])
			print type(thread_num)
		except:
			thread_num = 2

		from accounts.models import Patron, Address
		self.product_links = {}

		# Get the user
		try:
			self.patron = Patron.objects.get(username='Axxlocation')
		except Patron.DoesNotExist:
			print "Can't find user 'Axxlocation'"
			return

		# Get the default address of the user to add to the product
		self.address = self.patron.default_address or self.patron.addresses.all()[0]

		# Configure the parser
		with closing(urlopen(self.base_url)) as main_page:
			self.soup = BeautifulSoup(main_page, 'html.parser')

		# Get families list of products
		self.product_families = [
		'/brh-brise-roche-hydraulique/',
		'/cisaille-a-beton/',
		'/cisaille-a-ferraille/',
		'/combi-pour-arden-20t/',
		'/decolleuse-pour-800-kg/',
		'/pince-de-tri/',
		'/mesure-et-signalisation/',
		'/modulaires/',
		'/sanitaires/',
		'/echafaudages/',
		'/nacelles-et-camion-nacelles/',
		'/chariot-elevateur/',
		'/telescopique/',
		'/cylindre/',
		'/patin-vibrant-pilloneuse-plaque-vibrante/',
		'/pied-de-mouton/',
		'/chargeuse-articulee/',
		'/dumper/',
		'/mini-chargeur/',
		'/mini-pelle/',
		'/chauffage-a-air-pulse/',
		'/compresseurs/',
		'/deshumidificateur/',
		'/groupes-electrogenes/',
		'/camion-refrigere/',
		'/remorque-tribune/',
		'/structures-gonflables/',
		'/vehicule-prestige/',
		'/coupe-et-poncage/',
		'/nettoyage-et-decoration/',
		'/traitement-du-beton/',
		'/pelleteuses/',
		'/outils-de-demolition-materiel-a-la-vente/',
		'/camions-bennes-3t5/',
		'/remorques-tp/'
		]
		# self.product_families = self.soup.findAll('a', href=re.compile('famille'))
		
		# List the products
		for i in xrange(thread_num):
			threading.Thread(target=self._subpage_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()

		print 'Found %d object' % len(self.product_links)

		# Create the products in the database
		for i in xrange(thread_num):
			threading.Thread(target=self._product_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()