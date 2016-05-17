	from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing

import threading

category_mapping = {
	# Art de la table
	'/les-forfaits-vaiselle-48/': 'assiettes-et-sous-assiettes',
	# Verre/Verrie
	'/coupes-flutes-45/': 'verrerie',
	'/verres-divers-47/': 'verrerie',
	'/verrerie-87/': 'verrerie',
	'/verres-a-vin-eau-46/': 'verrerie',
	# Assiettes
	'/assiette-oslo-69/': 'assiettes-et-sous-assiettes',
	'/assiette-victoria-41/': 'assiettes-et-sous-assiettes',
	'/assiette-muse-guy-degrenne-40/': 'assiettes-et-sous-assiettes',
	'/assiette-filet-d-or-39/': 'assiettes-et-sous-assiettes',
	'/tasses-et-sous-tasses-43/': 'assiettes-et-sous-assiettes',
	'/assiette-autres-68/': 'assiettes-et-sous-assiettes',
	'/bols-42/': 'assiettes-et-sous-assiettes',
	# Les couverts
	'/couverts-standard-70/': 'couverts',
	'/couverts-prestige-71/': 'couverts',
	'/astree-cisele-guy-degrenne-97/': 'couverts',
	'/fourchettes-36/': 'couverts',
	'/couteaux-37/': 'couverts',
	'/cuilleres-38/': 'couverts',
	'/divers-62/': 'couverts',
	'/pour-fruits-de-mer-64/': 'couverts',
	# Accessoires de table
	'/mat-riel-inox-alu-83/': 'les-contenants-et-lutilitaire',
	'/accessoires-86/': 'les-contenants-et-lutilitaire',
	'/corbeille-a-pain-30/': 'les-contenants-et-lutilitaire',
	'/chandelier-32/': 'les-contenants-et-lutilitaire',
	'/presentoir-35/': 'les-contenants-et-lutilitaire',
	# Cuisine
	# Materiel alimentaire
	'/bouilloire-cafetiere-75/': 'cafetiere',
	'/plancha-crepe-gauffre-raclette-76/': 'grill-pierrade',
	'/friteuse-barbecue-77/': 'friteuse',
	'/cuisson-festive-gourmande-82/': 'fontaine-chocolat',
	'/machine-boisson-glacon-84/': 'machine-a-glace',
	'/mat-riel-a-viande-85/': 'trancheur-de-jambon',
	# Cuisson rechauffe
	'/cuisson-rechauffe-12/': 'cuiseur-vapeur',
	# Refrigerateur
	'/r-frig-rateur-congelateur-72/': 'congelateur',
	# Materiel cuisine
	'/mat-riel-de-cuisine-73/': 'les-contenants-et-lutilitaire',
	# Ustensile  de cuisine
	'/ustensile-de-cuisine-74/': 'divers',
	# Plat gastronomique
	'/plat-bac-gastronomique-34/': 'bac-gastro',
	# Consommables
	'/consommables-11/': 'decoration',
	# Evenementiel
	'/mobilier-evenementiel-93/': 'meuble',
	'/mobilier-evenementiel-93/page-2.html': 'meuble',
	'/decors-evenementiel-50/': 'decoration',
	'/prestations-evenementielles-58/': 'jeux-de-bistrot',
	'/structures-gonflables-89/': 'jeux-dadresse',
	'/stands-forains-90/': 'jeux/jeux-de-bistrot',
	'/stands-forains-90/page-2.html': 'jeux/jeux-de-bistrot',
	'/jeux-de-bois-geant-91/': 'jeux-de-societe',
	# Mobilier-Chapiteaux
	'/chaise-banc-salon-club-79/': 'chaises',
	'/mange-debout-gueridon-tabouret-80/': 'tables-et-buffets',
	'/table-19/': 'tables-et-buffets',
	'/nappage-21/': 'nappes',
	'/mobilier-lumineux-81/',
	'/mobilier-evenementiel-66/',
	'/mobilier-evenementiel-66/page-2.html',
	'/divers-20/': 'divers',
	'/chapiteaux-barnum-78/': 'chapiteau',
	# Chapiteaux Barum
	'/barnum-tente-pliante-94/': 'chapiteau',
	'/toilette-95/': 'toilette-bebe',
	'/chapiteaux-96/': 'chapiteau',
	'/chauffage-8/': 'chauffage',
}

class Command(BaseCommand):
    help = 'Imports Alpha Reception'

    base_url = 'http://www.alpha-reception.com'

    thread_num = 1

    username = 'alphareception'

    # For Test
    #username = 'benoit'

    product_list_tag = {
		"name": "div",
		"attrs": {
			"class": "bloc-produit"
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
			"border": "0"
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
				print "image_url : %s" % image_url
			except Exception, e:
				print "pass image: %s" % str(e)
				pass

			#Get the title
			try:
				summary = product_soup.find(self.summary_tag["name"], self.summary_tag["attrs"]).text
				print "summary : %s" % summary
			except Exception, e:
				print "pass title: %s" % str(e)
				pass


			#Get the description and price
			try:
				union_list_tmp = product_soup.find(self.description_tag["name"], self.description_tag["attrs"])
				description = union_list_tmp.find("div")
				price = description.find_next("div").text
				print description.text
				print price.split(' ', 1)[0]

				#print "description : %s" % description
			except Exception, e:
				description = " "
				print "pass description: %s" % str(e)
				pass


			# deposit_amount = 0.0

			# from products.models import Category, Price
			# from products.choices import UNIT
			# print category_mapping[category]
			# try:
			# 	product = Product.objects.create(
			# 		summary=summary, description=description,
			# 		deposit_amount=deposit_amount, address=self.address, owner=self.patron,
			# 		category=Category.objects.get(slug=category_mapping[category]), is_allowed=False
			# 	)

			# 	try:
			# 		with closing(urlopen(image_url)) as image:
			# 			product.pictures.add(Picture.objects.create(
			# 				image=uploadedfile.SimpleUploadedFile(
			# 					name='img', content=image.read())
			# 				)
			# 			)
			# 	except HTTPError as e:
			# 		print '\nerror loading image for object at url:', self.base_url + product_url

			# except Exception, e:
			# 	print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
			# 	print 'error: %s' % str(e)
			# 	pass


    def handle(self, *args, **options):
    	from accounts.models import Patron, Address

        self.product_links = {}

        self.product_families = [
        	# Art de la table
        	# Les forfait vaiselle
			'/les-forfaits-vaiselle-48/',
			# Verre/Verrie
			'/coupes-flutes-45/',
			'/verres-divers-47/',
			'/verrerie-87/',
			'/verres-a-vin-eau-46/',
			# Assiettes
			'/assiette-oslo-69/',
			'/assiette-victoria-41/',
			'/assiette-muse-guy-degrenne-40/',
			'/assiette-filet-d-or-39/',
			'/tasses-et-sous-tasses-43/',
			'/assiette-autres-68/',
			'/bols-42/',
			# Les couverts
			'/couverts-standard-70/',
			'/couverts-prestige-71/',
			'/astree-cisele-guy-degrenne-97/',
			'/fourchettes-36/',
			'/couteaux-37/',
			'/cuilleres-38/',
			'/divers-62/',
			'/pour-fruits-de-mer-64/',
			# Accessoires de table
			'/mat-riel-inox-alu-83/',
			'/accessoires-86/',
			'/corbeille-a-pain-30/',
			'/chandelier-32/',
			'/presentoir-35/',
			# Cuisine
			# Materiel alimentaire
			'/bouilloire-cafetiere-75/',
			'/plancha-crepe-gauffre-raclette-76/',
			'/friteuse-barbecue-77/',
			'/cuisson-festive-gourmande-82/',
			'/machine-boisson-glacon-84/',
			'/mat-riel-a-viande-85/',
			# Cuisson rechauffe
			'/cuisson-rechauffe-12/',
			# Refrigerateur
			'/r-frig-rateur-congelateur-72/',
			# Materiel cuisine
			'/mat-riel-de-cuisine-73/',
			# Ustensile  de cuisine
			'/ustensile-de-cuisine-74/'
			# Plat gastronomique
			'/plat-bac-gastronomique-34/',
			# Consommables
			'/consommables-11/',
			# Evenementiel
			'/mobilier-evenementiel-93/',
			'/decors-evenementiel-50/',
			'/prestations-evenementielles-58/',
			'/structures-gonflables-89/',
			'/stands-forains-90/',
			'/stands-forains-90/page-2.html',
			'/jeux-de-bois-geant-91/',
			# Mobilier-Chapiteaux
			'/chaise-banc-salon-club-79/',
			'/mange-debout-gueridon-tabouret-80/',
			'/table-19/',
			'/nappage-21/',
			'/mobilier-lumineux-81/',
			'/mobilier-evenementiel-66/',
			'/mobilier-evenementiel-66/page-2.html',
			'/divers-20/',
			'/chapiteaux-barnum-78/',
			# Chapiteaux Barum
			'/barnum-tente-pliante-94/',
			'/toilette-95/',
			'/chapiteaux-96/',
			'/chauffage-8/',
        ]

        # Get the user
   #      try:
   #      	self.patron = Patron.objects.get(username=self.username)
   #      except Patron.DoesNotExist:
			# print "Can't find user 'clownmont'"
			# return

   #      self.address = self.patron.default_address or self.patron.addresses.all()[0]

        self._subpage_crawler()
        self._product_crawler()
  #       for i in xrange(self.thread_num):
  #       	threading.Thread(target=self._subpage_crawler).start()
  #       for thread in threading.enumerate():
  #       	if thread is not threading.currentThread():
  #       		thread.join()

		# # Create the products in the database
		# for i in xrange(self.thread_num):
		# 	threading.Thread(target=self._product_crawler).start()
		# for thread in threading.enumerate():
		# 	if thread is not threading.currentThread():
		# 		thread.join()
