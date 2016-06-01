# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing
from decimal import Decimal

import threading

category_mapping = {
	# Alimenter - Stocker 
	'78-alimenter-en-electricite': 'outillage-depannage',
	'79-cuve-fioul': 'groupe-electrogene',
	'121-alimenter-en-air': 'arrosoir-de-jardin-seau',
	# Chauffer - Assecher 
	'81-assecher': 'chauffage',
	'82-ventiler': 'ventilateur',
	'84-chauffer': 'chauffage',
	# Compacter 
	'85-terrassement': 'pelle-pioche-et-tariere',
	'86-mesurer': 'laser-de-mesure',
	# consommables
	'77-consommables?id_category=77&n=50': 'divers',
	# Decorer - Entretenir - Souder
	'87-souder': 'divers',
	'83-decouper': 'carrelette',
	'123-decoration': 'divers',
	'124-entretien': 'divers',
	# engins-batiment-travaux-publique
	'89-minipelle?id_category=89&n=20': 'travaux',
	'90-minichargeur': 'travaux',
	'91-dumper': 'travaux',
	'92-rouleau-vibrant': 'travaux',
	'93-plaque-vibrante': 'travaux',
	'130-accessoires-engins-de-travaux-publics?id_category=130&n=20': 'travaux',
	# evenementiel
	'76-evenementiel': 'constructions-modulaires',
	# Jardiner
	'94-nettoyer': 'aspirateur',
	'95-entretien?id_category=95&n=20': 'motobineuse-et-motoculteur',
	'96-tailler': 'taille-haie',
	'97-decouper': 'tronconneuse-a-metaux',
	'98-preparer-la-terre': 'motobineuse-et-motoculteur',
	'132-accessoires-d-engins-de-travaux-public-et-terrassement': 'pelle-pioche-et-tariere',
	# Nettoyer-Decaper-Pomper
	'99-nettoyer?id_category=99&n=20': 'nettoyeur-haute-pression',
	'100-pomper': 'pompe-submersible',
	'118-aspirer-souffler': 'aspirateur',
	'125-decaper': 'aspirateur-industriel',
	# Signaler-Securiser-Eclairer
	'101-securiser?id_category=101&n=20': 'cloisons-et-paravents',
	'102-eclairer': 'constructions-modulaires',
	'103-communiquer': 'talkie-walkie',
	'104-signaler?id_category=104&n=20': 'travaux',
	# Traiter le beton
	'143-casser?id_category=143&n=50': 'compresseur',
	'133-decouper': 'meuleuse',
	'88-perforer': 'perceuse-filaire',
	'134-poncer': 'ponceuse',
	'135-preparer-le-beton?id_category=135&n=50': 'outillage-de-demolition',
	'136-vibrer': 'outillage-de-demolition',
	'144-forer': 'scie-circulaire',
	# Traiter le placo
	'137-decouper': 'scie-circulaire',
	'138-fixer': 'perceuse-a-main',
	'139-perforer': 'perceuse-filaire',
	'140-poncer': 'defonceuse',
	'141-visser-devisser': 'compresseur',
	# Transport - Lever - Manutentionner
	'105-manutentionner': 'travaux',
	'106-lever': 'treuil-et-palan',
	'108-remorquer': 'travaux',
	'126-tirer': 'travaux',
	'145-accesoires-de-levage': 'travaux',
	#  Travailler en equipe
	'109-echafaudage': 'echafaudage',
	'110-pir': 'echafaudage',
	'111-echelle': 'echelle',
	'112-tretaux': 'table-a-tapisser',
}

class Command(BaseCommand):
    help = 'Imports Klm-Location'

    base_url = 'http://www.klm-location.com/'

    thread_num = 1

    #username = 'klmlocation'

    # For Test
    username = 'test123'

    product_list_tag = {
		"name": "li",
		"attrs": {
			"class": "ajax_block_product"
		}
	}

    product_url_tag = {
    	"name": "a",
		"attrs": {
			"class": "product_img_link"
		}
    }

    image_url_tag = {
    	"name": "img",
		"attrs": {
			"id": "bigpic"
            }
        }


    description_tag = {
		"name": "div",
		"attrs": {
			"id": "short_description_content"
		}
	}
    summary_tag = {
		"name": "title",
		"attrs": {
			"class": "navigation-pipe"
		}
	}

    price_tag = {
		"name": "td",
		"attrs": {
			"width": "78"
		}
	}

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
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
                	#print product_url

    def _product_crawler(self):
    	from products.models import Product, Picture, Price
    	
    	#Entry url : ../photos/articles/mediums/263.jpg
    	#Out url : http://www.alpha-reception.com/photos/articles/mediums/263.jpg
    	def get_right_img_url(img_url):
    		return self.base_url + '/' + image_url[3:]

    	def _to_decimal(str):
    		from decimal import Decimal as D
    		return D(str.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))


    	while True:
			try:
				product_url, category = self.product_links.popitem()
				#print "product_url : %s" % product_url
			except KeyError:
				break

			try:
				with closing(urlopen(product_url)) as product_page:
					product_soup = BeautifulSoup(product_page, 'html.parser')
			except HTTPError:
				print 'error loading page for object at url', product_url

			#Get the image
			try:
				image_url = product_soup.find(self.image_url_tag["name"], self.image_url_tag["attrs"]).get('src')
				#image_url = get_right_img_url(image_url)
				#print "image_url : %s" % image_url
			except Exception, e:
				image_url = None
				print "pass image: %s" % str(e)
				pass

			#Get the title
			try:
				summary = product_soup.find(self.summary_tag["name"]).text
				#print "summary : %s" % summary
			except Exception, e:
				summary = None
				print "pass title: %s" % str(e)
				pass


			#Get the description
			try:
				description = product_soup.find(self.description_tag["name"], self.description_tag["attrs"]).text
				#print "description : %s" % description
			except Exception, e:
				description = None
				print "pass description: %s" % str(e)
				pass


			# Get the price
			try:
				price = product_soup.find(self.price_tag["name"], self.price_tag["attrs"]).text
				price = Decimal(price.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))
				#print 'price : %s' % price
			except:
				price = None
				print "price error %s" % product_url
				pass


			deposit_amount = 0.0

			from products.models import Category, Price
			from products.choices import UNIT
			#print category_mapping[category]
			try:
				product = Product.objects.create(
					summary=summary, description=description,
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
				except HTTPError as e:
					print '\nerror loading image for object at url:', self.base_url + product_url

				if price:
					try:
						product.prices.add(Price(amount=price, unit=UNIT.DAY))
					except Exception, e:
						print 'PRICE ERROR'
						pass

			except Exception, e:
				print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
				print 'error: %s' % str(e)
				pass


    def handle(self, *args, **options):
    	from accounts.models import Patron, Address

        self.product_links = {}

        self.product_families = [
        	# Alimenter - Stocker 
			# '78-alimenter-en-electricite',
			# '79-cuve-fioul',
			# '121-alimenter-en-air',
			# # Chauffer - Assecher 
			# '81-assecher',
			# '82-ventiler',
			# '84-chauffer',
			# # Compacter 
			# '85-terrassement',
			# '86-mesurer',
			# consommables
			'77-consommables?id_category=77&n=50',
			# # Decorer - Entretenir - Souder
			# '87-souder',
			# '83-decouper',
			# '123-decoration',
			# '124-entretien',
			# # engins-batiment-travaux-publique
			#  '89-minipelle?id_category=89&n=20',
			# '90-minichargeur',
			# '91-dumper',
			# '92-rouleau-vibrant',
			# '93-plaque-vibrante',
			# '130-accessoires-engins-de-travaux-publics?id_category=130&n=20',
			# # evenementiel
			# '76-evenementiel',
			# # Jardiner
			# '94-nettoyer',
			# '95-entretien?id_category=95&n=20',
			# '96-tailler',
			# '97-decouper',
			# '98-preparer-la-terre',
			# '132-accessoires-d-engins-de-travaux-public-et-terrassement',
			# # Nettoyer-Decaper-Pomper
			# '99-nettoyer?id_category=99&n=20',
			# '100-pomper',
			# '118-aspirer-souffler',
			# '125-decaper',
			# # Signaler-Securiser-Eclairer
			# '101-securiser?id_category=101&n=20',
			# '102-eclairer',
			# '103-communiquer',
			# '104-signaler?id_category=104&n=20',
			# # Traiter le beton
			# '143-casser?id_category=143&n=50',
			# '133-decouper',
			# '88-perforer',
			# '134-poncer',
			# '135-preparer-le-beton?id_category=135&n=50',
			# '136-vibrer',
			# '144-forer',
			# # Traiter le bois
			# '137-decouper',
			# '138-fixer',
			# '139-perforer',
			# '140-poncer',
			# '141-visser-devisser',
			# # Transport - Lever - Manutentionner
			# '105-manutentionner',
			# '106-lever',
			# '108-remorquer',
			# '126-tirer',
			# '145-accesoires-de-levage',
			# #  Travailler en equipe
			# '109-echafaudage',
			# '110-pir',
			# '111-echelle',
			# '112-tretaux',
        ]

        #Get the user
        try:
        	self.patron = Patron.objects.get(username=self.username)
        except Patron.DoesNotExist:
			print "Can't find user 'alphareception'"
			return

        self.address = self.patron.default_address or self.patron.addresses.all()[0]

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
