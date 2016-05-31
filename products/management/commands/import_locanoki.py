# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing
from decimal import Decimal as D

import threading

category_mapping = {
	# Construction/Renovation
	'location-materiel-construction-amenagement-renovation-lille/menuiserie-travail-du-bois.html': 'travaux',
	'location-materiel-construction-amenagement-renovation-lille/renovation.html': 'travaux',
	'location-materiel-construction-amenagement-renovation-lille/nettoyage.html': 'aspirateur',
	'location-materiel-construction-amenagement-renovation-lille/peinture-et-projection.html': 'travaux',
	'location-materiel-construction-amenagement-renovation-lille/travail-en-hauteur.html': 'echelle',
	'location-materiel-construction-amenagement-renovation-lille/bricolage-jardin.html': 'motobineuse-et-motoculteur',
	# Energie et air
	'location-materiel-energie-et-air-lille/location-compresseurs.html': 'compresseur',
	'location-materiel-energie-et-air-lille/location-groupes-electrogenes.html': 'groupe-electrogene',
	'location-materiel-energie-et-air-lille/location-eclairage-lille.html': 'spot',
	# Transport / Manutention
	'location-transport-et-manutention-lille/remorques.html': 'remorque-utilitaire',
	'location-transport-et-manutention-lille/materiel-de-manutention.html': 'travaux',
	# Evenement / Reception
	'location-materiel-evenement-et-reception-lille/location-tables-et-chaises.html': 'meuble',
	'location-materiel-evenement-et-reception-lille/location-mobilier-de-decoration.html': 'decoration',
	'location-materiel-evenement-et-reception-lille/location-nappes-housses.html': 'nappes',
	'location-materiel-evenement-et-reception-lille/location-podium.html': 'decoration',
	'location-materiel-evenement-et-reception-lille/location-chapiteau.html': 'chapiteau',
	'location-materiel-evenement-et-reception-lille/location-materiel-images-et-sono.html': 'effets-son',
	'location-materiel-evenement-et-reception-lille/location-materiel-images-et-sono.html?start=20': 'effets-son',
	'location-materiel-evenement-et-reception-lille/location-materiel-images-et-sono.html?start=40': 'effets-son',
	'location-materiel-evenement-et-reception-lille/location-chateau-gonflable-lille.html': 'jeux-gonflables',
}

class Command(BaseCommand):
    help = 'Imports Loca Noki'

    base_url = 'http://www.locanoki.fr/'

    thread_num = 1

    username = 'locanoki'

    # For Test
    #username = 'test123'

    product_list_tag = {
		"name": "div",
		"attrs": {
			"class": "djc_item_in"
		}
	}

    product_url_tag = {
    	"name": "a",
		"attrs": {
			"class": "readmore"
		}
    }

    image_url_tag = {
    	"name": "div",
		"attrs": {
			"class":"djc_thumbnail"
            }
        }

    description_tag = {
		"name": "div",
		"attrs": {
			"class": "djc_fulltext"
		}
	}
    summary_tag = {
		"name": "h2",
		"attrs": {
			"class": "djc_title"
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
    	

    	def get_price_range(str, begin, end):
    		while True:
    			end -= 1
    			if str[end].isdigit() == True or str[end] == ',':
    				continue
    			else:
    				begin = end
    				return begin

    	while True:
			try:
				product_url, category = self.product_links.popitem()
				#print "product_url : %s" % product_url
			except KeyError:
				break

			try:
				with closing(urlopen(self.base_url + product_url)) as product_page:
					product_soup = BeautifulSoup(product_page, 'html.parser')
			except HTTPError:
				print 'error loading page for object at url', product_url



			#Get the title
			try:
				summary = product_soup.find(self.summary_tag["name"], self.summary_tag["attrs"]).text
				summary = summary.strip(' ')
				#print "summary : %s" % summary.strip(' ')
			except Exception, e:
				summary = " "
				print "pass title: %s" % str(e)
				pass


			#Get the image
			try:
				image_urls = product_soup.find_all(self.image_url_tag["name"], self.image_url_tag["attrs"])
			except Exception, e:
				image_urls = None
				print "pass image: %s" % str(e)
				pass



			#Get the description
			try:
				description = product_soup.find(self.description_tag["name"], self.description_tag["attrs"]).text
				#print "description : %s" % description
			except Exception, e:
				description = " "
				print "pass description: %s" % str(e)
				pass

			#Get the Price	
			price_pos = description.find(u'€')
			if price_pos == -1:
				price = None
			else:
				price = description[get_price_range(description, 0, price_pos):price_pos]
				price = (price.strip().replace(u'€', '').replace(',', '.').replace(' ', '').replace(':', ''))
				#print price


			deposit_amount = 0.0


			from products.models import Category, Price
			from products.choices import UNIT
			try:
				product = Product.objects.create(
					summary=summary, description=description,
					deposit_amount=deposit_amount, address=self.address, owner=self.patron,
					category=Category.objects.get(slug=category_mapping[category]), is_allowed=False
				)


				if image_urls:
					try:
						for image_url in image_urls:
							with closing(urlopen(image_url.find('a').get('href'))) as image:
								product.pictures.add(Picture.objects.create(
									image=uploadedfile.SimpleUploadedFile(
										name='img', content=image.read())
								)
							)
					except HTTPError as e:
						print '\nerror loading image for object at url:', self.base_url + product_url

				# Add the price to the product
				try:
					if price:
						product.prices.add(Price(amount=price, unit=UNIT.DAY))
				except:
					print 'PRICE ERROR'
					print product_url
					pass

			except Exception, e:
				print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
				print 'error: %s' % str(e)
				pass


    def handle(self, *args, **options):
    	from accounts.models import Patron, Address

        self.product_links = {}

        self.product_families = [
        	# Construction/Renovation
        	'location-materiel-construction-amenagement-renovation-lille/menuiserie-travail-du-bois.html',
        	'location-materiel-construction-amenagement-renovation-lille/renovation.html',
        	'location-materiel-construction-amenagement-renovation-lille/nettoyage.html',
        	'location-materiel-construction-amenagement-renovation-lille/peinture-et-projection.html',
        	'location-materiel-construction-amenagement-renovation-lille/travail-en-hauteur.html',
        	'location-materiel-construction-amenagement-renovation-lille/bricolage-jardin.html',
        	# Energie et air
        	  'location-materiel-energie-et-air-lille/location-compresseurs.html',
        	 'location-materiel-energie-et-air-lille/location-groupes-electrogenes.html',
        	'location-materiel-energie-et-air-lille/location-eclairage-lille.html',
        	# Transport / Manutention
        	'location-transport-et-manutention-lille/remorques.html',
        	'location-transport-et-manutention-lille/materiel-de-manutention.html',
        	# Evenement / Reception
        	'location-materiel-evenement-et-reception-lille/location-tables-et-chaises.html',
        	'location-materiel-evenement-et-reception-lille/location-mobilier-de-decoration.html',
        	'location-materiel-evenement-et-reception-lille/location-nappes-housses.html',
        	'location-materiel-evenement-et-reception-lille/location-podium.html',
        	'location-materiel-evenement-et-reception-lille/location-chapiteau.html',
        	'location-materiel-evenement-et-reception-lille/location-materiel-images-et-sono.html',
        	'location-materiel-evenement-et-reception-lille/location-materiel-images-et-sono.html?start=20',
        	'location-materiel-evenement-et-reception-lille/location-materiel-images-et-sono.html?start=40',
        	'location-materiel-evenement-et-reception-lille/location-chateau-gonflable-lille.html',
        ]

        # Get the user
        try:
        	self.patron = Patron.objects.get(username=self.username)
        except Patron.DoesNotExist:
			print "Can't find user 'locanoki'"
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
