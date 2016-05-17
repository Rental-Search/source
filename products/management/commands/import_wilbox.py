from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing

import simplejson as json

class Command(BaseCommand):

    help = 'Imports Wilbox'

    # For test
    #username = 'arclite'
    username = 'Wilbox'

    base_url = 'http://www.wilbox.fr/locationjeux/svc_all.php?filterscount=0&groupscount=0&pagenum=0&pagesize=10&recordstartindex=0&recordendindex=8.666666666666668'

    # 2 Size image : th and med
    image_th_base_url = 'http://www.wilbox.fr/inc/clt/img/data/jeu/th/'
    image_med_base_url = 'http://www.wilbox.fr/inc/clt/img/data/jeu/med/'


    # Product category
    category = 'jeux-de-societe'

    def _get_Wilbox_Json(self):
    	with closing(urlopen(self.base_url)) as products_json_data:
    		self.products = json.load(products_json_data)

    def _get_products(self):
    	from products.models import Product, Picture, Price

    	for x in xrange(len(self.products['data'])):

    		# Get the product title
    		summary = self.products['data'][x]['title_article'];

    		# Get the product price
    		price = self.products['data'][x]['prix']

    		# Get the product description
    		nb_player = 'Nombre de joueurs: ' + self.products['data'][x]['nbjoueursmin'] + '-' + self.products['data'][x]['nbjoueursmax'] + '\n'
    		game_time = 'Temps(minutes): ' + self.products['data'][x]['temps_minutes'] + '\n'
    		age_min = 'Age minimum: ' + self.products['data'][x]['agemin'] + '\n'
    		game_genre = 'Genre: ' + self.products['data'][x]['title_genre'] + '\n'
    		description = nb_player + game_time + age_min + game_genre + self.products['data'][x]['descr']
    		#print description

    		# Get the product image
    		image_url = self.image_med_base_url + self.products['data'][x]['imgsrc']

    		deposit_amount = 0.0
    		from products.models import Category
    		from products.choices import UNIT

    		try:
    			product = Product.objects.create(
    				summary=summary, description=description,
    				deposit_amount=deposit_amount, address=self.address, owner=self.patron,
    				category=Category.objects.get(slug=self.category)
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
    				print summary

    			try:
    				product.prices.add(Price(amount=price, unit=UNIT.DAY))
    			except Exception, e:
    				print 'PRICE ERROR'
    				pass


    		except Exception, e:
    			print 'CANNOT CREATE THE PRODUCT %s \n' % (summary)
    			print 'error: %s' % str(e)
    			break

    def handle(self, *args, **options):
    	from accounts.models import Patron, Address

    	self.products = {}

    	# Get the user
    	try:
    		self.patron = Patron.objects.get(username=self.username)
    	except Patron.DoesNotExist:
    		print "Can't find user 'wilbox'"
    		return

    	self.address = self.patron.default_address or self.patron.addresses.all()[0]

    	self._get_Wilbox_Json()
    	self._get_products()

    	