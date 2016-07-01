# coding=utf-8
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from bs4 import BeautifulSoup
from contextlib import closing
from urllib2 import urlopen
from django.core.files import uploadedfile

category_mapping = {
# Gonflables
'/les-gonflables/location-chateau-gonflable-parcours-piscine-a-balles-toboggan/': 'jeux-gonflables',
'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/': 'jeux-gonflables',
'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/jeux-sports-extremes/': 'jeux-gonflables',
	'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/jeux-thème-foot/': 'jeux-gonflables',
	'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/jeux-thème-rugby/': 'jeux-gonflables',

	# Materiel de reception
	'/materiel-de-reception/tentes-tables-chaises/': 'jeux-gonflables',
	'/materiel-de-reception/machines/': 'jeux-gonflables',
	'/materiel-de-reception/pack-reception/': 'jeux-gonflables',

	#Evénementiel publicitaire
	'/autres-jeux/location-rosalie/': 'jeux',
	'/les-gonflables/gonflable-publicitaire-arche-sky-dancer-père-noël-gonflable/': 'jeux-gonflables',

	# Animations
	'/animations/discomobile/': 'jeux',
	'/animations/animation-mariage/': 'jeux',
	'/animations/location-chateau-gonflable-lion/karaoké-pro/': 'jeux',

	#Autres jeux
	'/autres-jeux/': 'jeux',

	#Pack sportifs
	'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/packs-jeux-intervillages/': 'jeux-gonflables',
	}

class Command(BaseCommand):
	help = "Import Animadoc"

	base_url = "http://www.animadoc.info/"

	username = 'animadoc'

	nb_product = 0

	product_tag = {
		"name": "div",
		"attrs": {
			"class": "clearover"
		},
		"second_name": "div",
		"second_attrs":{
			"class": "align-container imgleft"
		}
	}

	sub_product_ulr = {
		"name": "a",
		"attrs": {
			"class":"imagewrapper"
		}
	}
		
	image_tag = {
		"name": "a",
		"attrs": {
			"class": "imagewrapper"
		},
		"second_name": "img",
		"second_attrs": {
			"style": "width:100%"
		}
	}

	description_tag = {
		"name": "p",
		"attrs": {
			"style":"text-align: center;"
		}
	}




	def handle(self, *args, **options):
		# Get User
		from accounts.models import Patron, Address
		try:
			self.patron = Patron.objects.get(username=self.username)
		except Patron.DoesNotExist:
			print "Can't find user 'Animadoc'"
			return

		# Get user address
		self.address = self.patron.default_address or self.patron.addresses.all()[0]

		self.product_families = [
		# Gonflables
		'/les-gonflables/location-chateau-gonflable-parcours-piscine-a-balles-toboggan/',
		'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/',
		'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/jeux-sports-extremes/',
		'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/jeux-thème-foot/',
		'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/jeux-thème-rugby/',

		# Materiel de reception
		'/materiel-de-reception/tentes-tables-chaises/',
		'/materiel-de-reception/machines/',
		'/materiel-de-reception/pack-reception/',

		# Evénementiel publicitaire
		'/autres-jeux/location-rosalie/',
		'/les-gonflables/gonflable-publicitaire-arche-sky-dancer-père-noël-gonflable/',

		# Animations
		'/animations/discomobile/',
		'/animations/animation-mariage/',
		'/animations/location-chateau-gonflable-lion/karaoké-pro/',

		#Autres jeux
		'/autres-jeux/',

		#Pack sportifs
		'/les-gonflables/jeux-gonflable-sportif-sumos-joutes-baby-foot-parcours-géant/packs-jeux-intervillages/',

		]


		delivery_info = u'\nLIVRAISON: 20km de DAUX (31) gratuit + 20km = 1€/km (Aller et Retour compris)'
		deposit_info = u'\nCaution: 1000€'

		while True:
			try:
				family = self.product_families.pop()
				category = family
			except Exception, e:
				break

			with closing(urlopen(self.base_url + family)) as product_page:
				product_soup = BeautifulSoup(product_page, 'html.parser')

			# Get all div of products
			product_url = product_soup.find_all(self.product_tag['name'], self.product_tag['attrs'])

			for product in product_url:
				short_description = None
				summary = None
				image_url = None
				get_summary = False
				
				# Get image url of product
				try:
					image_url = product.find(self.image_tag['second_name'], self.image_tag['second_attrs']).get('src')
				except Exception, e:
					pass

				short_description = product.text + delivery_info + deposit_info
				short_description = short_description.strip()
				# if summary:
				#print "Summary : %s " % summary
				
				# if short_description and short_description.strip() and image_url:
				# 	print "Description %s" % short_description
				# 	print "Summary %s" % short_description.split('\n', 1)[0]
				from products.models import Category, Price
				from products.choices import UNIT
				from products.models import Product, Picture, Price

				deposit_amount = 1000.0

				if short_description and short_description.strip() and image_url:
					summary = short_description.split('\n', 1)[0]
					try:
						product = Product.objects.create(
							summary=summary, description=short_description,
							deposit_amount=deposit_amount, address=self.address, owner=self.patron,
							category=Category.objects.get(slug=category_mapping[category]), is_allowed=False
							)

						try:
							with closing(urlopen(image_url)) as image:
								product.pictures.add(Picture.objects.create(
									image=uploadedfile.SimpleUploadedFile(
										name='img', content=image.read())
									)
								)
						except Exception, e:
							print str(e)
							print image_url
							print 'Error loading image'
					except Exception, e:
						print str(e)
						pass

