from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing

import threading

category_mapping = {
	# Art de la table
	'/shop/art-de-la-table/accessoires-inox/': 'les-contenants-et-lutilitaire',
	'/shop/art-de-la-table/accessoires-verrerie/': 'verrerie',
	'/shop/art-de-la-table/assiettes/': 'assiettes-et-sous-assiettes',
	'/shop/art-de-la-table/couverts-en-inox/': 'couverts',
	'/shop/art-de-la-table/materiel-de-buffet/': 'les-contenants-et-lutilitaire',
	'/shop/art-de-la-table/plats-inox-et-alu/': 'plats-et-plateaux',
	'/shop/art-de-la-table/porcelaines/tasses/': 'verrerie',
	'/shop/art-de-la-table/verres/': 'verrerie',
	# Mobilier
	'/shop/mobilier/accessoires-mobilier/': 'divers',
	'/shop/mobilier/animations-exterieur/': 'barbecue',
	# Mobilier Chaise
	'/shop/mobilier/chaises/chaises-chaises/': 'chaises',
	'/shop/mobilier/chaises/fauteuils-et-canapes/': 'divers',
	'/shop/mobilier/chaises/poufs-et-bancs/': 'bar-et-tabourets',
	'/shop/mobilier/chaises/tabourets/': 'bar-et-tabourets',
	'/shop/mobilier/mange-debout-2/': 'comptoir',
	'/shop/mobilier/materiel-de-chauffage/': 'chauffage',
	'/shop/mobilier/materiel-hi-tech/': 'externe',
	'/shop/mobilier/mobilier-exterieur/': 'tente-de-reception',
	# Mobilier Lumineux
	'/shop/mobilier/mobilier-lumineux/bar-comptoir/': 'comptoir',
	'/shop/mobilier/mobilier-lumineux/cubes-lumineux/': 'led',
	'/shop/mobilier/mobilier-lumineux/led-divers/': 'led',
	'/shop/mobilier/mobilier-lumineux/mange-debout/': 'comptoir',
	# Mobilier Table
	'/shop/mobilier/tables/table-basse/': 'tables-et-buffets',
	'/shop/mobilier/tables/tables-ovales/': 'tables-et-buffets',
	'/shop/mobilier/tables/tables-rectangulaires/': 'tables-et-buffets',
	'/shop/mobilier/tables/tables-rondes/': 'tables-et-buffets',
	# Materiel traiteur Chaud
	'/shop/office-materiel-traiteur/chaud/maintien-au-chaud/': 'cuiseur-vapeur',
	'/shop/office-materiel-traiteur/chaud/materiel-a-gaz/': 'barbecue',
	'/shop/office-materiel-traiteur/chaud/materiel-electrique/': 'electromenager-de-cuisine',
	# Materiel traiteur Froid
	'/shop/office-materiel-traiteur/froid/accessoires-froid/': 'conteneur-isotherme',
	'/shop/office-materiel-traiteur/froid/materiel-electrique-2/': 'refrigerateur',
	# Materiel traiteur Office
	'/shop/office-materiel-traiteur/office/accessoires-osier/': 'ustensiles-de-table',
	'/shop/office-materiel-traiteur/office/divers/': 'plats-et-plateaux',
	'/shop/office-materiel-traiteur/office/ustensiles-de-cuisine/': 'plats-et-plateaux',
	# Decoration
	'/shop/decorations/chandeliers/': 'decoration',
	'/shop/decorations/compositions-florales/': 'decoration',
	'/shop/decorations/decorations-diverses/': 'decoration',
	'/shop/decorations/decorations-led/': 'decoration',
	# Nappage Houssse de chaise
	'/shop/nappage-housses-de-chaise/housses-de-chaises/': 'ustensiles-de-table',
	'/shop/nappage-housses-de-chaise/nappage/': 'ustensiles-de-table',
	'/shop/nappage-housses-de-chaise/rubans-pour-noeud-de-chaise/': 'ustensiles-de-table',
	'/shop/nappage-housses-de-chaise/serviettes/': 'ustensiles-de-table',
	# Consommables
	'/shop/consommables/': 'decoration',
	# Univers Led
	'/shop/univers-led/': 'led',
}

class Command(BaseCommand):
    help = 'Imports Centre Location Service'

    base_url = 'http://www.centre-location-service.com'

    thread_num = 1

    #username = 'centrelocationservices'

    # For Test
    username = 'benoit'

    product_list_tag = {
		"name": "li",
		"attrs": {
			"class": "product"
		}
	}

    product_url_tag = {
    	"name": "a",
		"attrs": {
			"class": "lnk_view"
		}
    }

    image_url_tag = {
    	"name": "img",
		"attrs": {
			"class": "attachment-shop_single"
            }
        }


    description_tag = {
		"name": "div",
		"attrs": {
			"class": "short-description"
		}
	}
    summary_tag = {
		"name": "h1",
		"attrs": {
			"class": "product_title"
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
    	
    	while True:
			try:
				product_url, category = self.product_links.popitem()
				print "product_url : %s" % product_url
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
				#print "image_url : %s" % image_url
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


			#Get the description
			try:
				description = product_soup.find(self.description_tag["name"], self.description_tag["attrs"]).text
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
        	# Art de la table
			'/shop/art-de-la-table/accessoires-inox/',
			'/shop/art-de-la-table/accessoires-verrerie/',
			'/shop/art-de-la-table/assiettes/',
			'/shop/art-de-la-table/couverts-en-inox/',
			'/shop/art-de-la-table/materiel-de-buffet/',
			'/shop/art-de-la-table/plats-inox-et-alu/',
			'/shop/art-de-la-table/porcelaines/tasses/',
			'/shop/art-de-la-table/verres/',
        	# Mobilier
        	'/shop/mobilier/accessoires-mobilier/',
        	'/shop/mobilier/animations-exterieur/',
			# Mobilier Chaise
			'/shop/mobilier/chaises/chaises-chaises/',
			'/shop/mobilier/chaises/fauteuils-et-canapes/',
			'/shop/mobilier/chaises/poufs-et-bancs/',
			'/shop/mobilier/chaises/tabourets/',
			'/shop/mobilier/mange-debout-2/',
			'/shop/mobilier/materiel-de-chauffage/',
			'/shop/mobilier/materiel-hi-tech/',
			'/shop/mobilier/mobilier-exterieur/',
			# Mobilier Lumineux
			'/shop/mobilier/mobilier-lumineux/bar-comptoir/',
			'/shop/mobilier/mobilier-lumineux/cubes-lumineux/',
			'/shop/mobilier/mobilier-lumineux/led-divers/',
			'/shop/mobilier/mobilier-lumineux/mange-debout/',
			# Mobilier Table
			'/shop/mobilier/tables/table-basse/',
			'/shop/mobilier/tables/tables-ovales/',
			'/shop/mobilier/tables/tables-rectangulaires/',
			'/shop/mobilier/tables/tables-rondes/',
			# Materiel traiteur Chaud
			'/shop/office-materiel-traiteur/chaud/maintien-au-chaud/',
			'/shop/office-materiel-traiteur/chaud/materiel-a-gaz/',
			'/shop/office-materiel-traiteur/chaud/materiel-electrique/',
			# Materiel traiteur Froid
			'/shop/office-materiel-traiteur/froid/accessoires-froid/',
			'/shop/office-materiel-traiteur/froid/materiel-electrique-2/',
			# Materiel traiteur Office
			'/shop/office-materiel-traiteur/office/accessoires-osier/',
			'/shop/office-materiel-traiteur/office/divers/',
			'/shop/office-materiel-traiteur/office/ustensiles-de-cuisine/',
			# Decoration
			'/shop/decorations/chandeliers/',
			'/shop/decorations/compositions-florales/',
			'/shop/decorations/decorations-diverses/',
			'/shop/decorations/decorations-led/',
			# Nappage Houssse de chaise
			'/shop/nappage-housses-de-chaise/housses-de-chaises/',
			'/shop/nappage-housses-de-chaise/nappage/',
			'/shop/nappage-housses-de-chaise/rubans-pour-noeud-de-chaise/',
			'/shop/nappage-housses-de-chaise/serviettes/',
			# Consommables
			'/shop/consommables/',
			# Univers Led
			'/shop/univers-led/',
        ]

        # Get the user
        try:
        	self.patron = Patron.objects.get(username=self.username)
        except Patron.DoesNotExist:
			print "Can't find user 'clownmont'"
			return

        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        #self._subpage_crawler()
        #self._product_crawler()
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
