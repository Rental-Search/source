# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing

import threading

category_mapping = {
	'/sablage-hydrogommage-115/': 'aspirateur-industriel',
	'/consommables-116/': 'divers',
	'/consommables-116/page-2.html': 'divers',
	'/betonnieres-92/': 'betonniere',
	'/application-beton-93/': 'regle-de-macon',
	'/carotage-94/': 'pelle-pioche-et-tariere',
	'/compresseur-117/': 'compresseur',
	'/marteau-pneumatique-89/': 'marteau-piqueur',
	'/marteau-electrique-90/': 'marteau-piqueur',
	'/materiels-de-mesure-detection-95/': 'detecteur-dhumidite',
	'/aspirateurs-66/': 'aspirateur',
	'/nettoyeurs-haute-pression-69/': 'nettoyeur-haute-pression',
	'/shampouineuses-71/': 'balayeuse',
	'/vehicules-74/': 'utilitaire',
	'/peinture-83/': 'outillage-electroportatif',
	'/decoration-84/': 'outillage-electroportatif',
	'/travail-du-bois-85/': 'coupe-bordure-et-cisaille-a-gazon',
	'/demenagement-80/': 'materiel-de-transport',
	'/camion-110/': 'utilitaire',
	'/nacelle-fleches-articulees-111/': 'travaux',
	'/plateforme-ciseaux-113/': 'travaux',
	'/nacelles-a-mats-114/': 'travaux',
	'/pompes-a-eau-96/': 'pompe-immergee',
	'/deboucheur-canalisation-97/': 'deboucheur',
	'/soudure-99/': 'poste-a-souder-a-flamme',
	'/plomberie-100/': 'outil-dassemblage-de-plombier',
	'/groupes-electrogenes-108/': 'groupe-electrogene',
	'/couper-scier-des-materiaux-102/': 'meuleuse',
	'/raboter-103/': 'cisaille-a-haie',
	'/echafaudage-105/': 'echafaudage',
	'/echafaudage-105/page-2.html': 'echafaudage',
	'/echelle-107/': 'echelle',
	'/remorque-benne-78/': 'porte-voiture',
	'/remorque-79/': 'remorque-utilitaire',
	'/minipelles-33/': 'pelle-pioche-et-tariere',
	'/chargeur-et-dumper-34/': 'outils-a-main',
	'/compactage-35/': 'pelle-pioche-et-tariere',
	'/demolition-87/': 'goulotte-devacuation',
	'/travailler-la-terre-60/': 'outils-a-moteur',
	'/tondre-61/': 'broyeur-de-vegetaux',
	'/jardinage-62/': 'aspirateur-et-souffleur',
	'/manutention-elevation-37/': 'travaux',
	'/chauffage-45/': 'chauffage',
	'/chauffage-45/page-2.html': 'chauffage',
	'/deshumidificateurs-47/': 'deshumificateur',
}

class Command(BaseCommand):
    help = 'Imports Alpha Location'

    base_url = 'http://www.alpha-location.fr'

    thread_num = 1

    username = 'alphalocation'

    # For Test
    #username = 'arclite'

    product_list_tag = {
		"name": "div",
		"attrs": {
			"class": "contenu_produit_liste"
		}
	}

    product_url_tag = {
    	"name": "a",
		"attrs": {
			"class": "produit-medium"
		}
    }

    image_url_tag = {
    	"name": "img",
		"attrs": {
			"vspace": "5"
            }
        }


    description_tag = {
		"name": "td",
		"attrs": {
			"width": "62%"
		}
	}
    summary_tag = {
		"name": "span",
		"attrs": {
			"class": "titre-article"
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

    def _product_crawler(self):
    	from products.models import Product, Picture, Price
    	

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
				image_url = get_right_img_url(image_url)
				print "image_url : %s" % image_url
			except Exception, e:
				print "pass image: %s" % str(e)
				pass

			#Get the title
			try:
				summary = product_soup.find(self.summary_tag["name"], self.summary_tag["attrs"]).text
				#print "summary : %s" % summary
			except Exception, e:
				print "pass title: %s" % str(e)
				pass


			#Get the description and price
			try:
				union_list_tmp = product_soup.find(self.description_tag["name"], self.description_tag["attrs"])
				description_tmp = union_list_tmp.find("div")
				price = description_tmp.find_next("div").text
				description = description_tmp.text
				price =  _to_decimal(price.split(' ', 1)[0])
				#print description
				#print price

				#print "description : %s" % description
			except Exception, e:
				description = " "
				print "pass description: %s" % str(e)
				pass


			deposit_amount = 0.0

			from products.models import Category, Price
			from products.choices import UNIT
			print category_mapping[category]
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

			except Exception, e:
				print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
				print 'error: %s' % str(e)
				pass


    def handle(self, *args, **options):
    	from accounts.models import Patron, Address

        self.product_links = {}

        self.product_families = [
        	# '/sablage-hydrogommage-115/',
        	# '/consommables-116/',
        	# '/consommables-116/page-2.html',
        	# '/betonnieres-92/',
        	# '/application-beton-93/',
        	# '/carotage-94/',
        	# '/marteau-pneumatique-89/',
        	# '/marteau-electrique-90/',
        	# '/materiels-de-mesure-detection-95/',
        	# '/aspirateurs-66/',
        	# '/nettoyeurs-haute-pression-69/',
        	# '/shampouineuses-71/',
        	# '/vehicules-74/',
        	# '/peinture-83/',
        	# '/decoration-84/',
        	# '/travail-du-bois-85/',
        	 '/demenagement-80/',
        	# '/camion-110/',
        	# '/nacelle-fleches-articulees-111/',
        	# '/plateforme-ciseaux-113/',
        	# '/nacelles-a-mats-114/',
        	# '/pompes-a-eau-96/',
        	# '/deboucheur-canalisation-97/',
        	# '/soudure-99/',
        	# '/plomberie-100/',
        	# '/groupes-electrogenes-108/',
        	# '/couper-scier-des-materiaux-102/',
        	# '/raboter-103/',
        	# '/echafaudage-105/',
        	# '/echafaudage-105/page-2.html',
        	# '/echelle-107/',
        	# '/remorque-benne-78/',
        	# '/remorque-79/',
        	# '/minipelles-33/',
        	# '/chargeur-et-dumper-34/',
        	# '/compactage-35/',
        	# '/demolition-87/',
        	# '/travailler-la-terre-60/',
        	# '/tondre-61/',
        	# '/jardinage-62/',
        	# '/manutention-elevation-37/',
        	# '/chauffage-45/',
        	# '/chauffage-45/page-2.html',
        	# '/deshumidificateurs-47/',
        ]

        #Get the user
        try:
        	self.patron = Patron.objects.get(username=self.username)
        except Patron.DoesNotExist:
			print "Can't find user 'alpha location"
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
