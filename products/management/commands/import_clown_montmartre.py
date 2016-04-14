from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, HTTPError
from contextlib import closing

import threading

category_mapping = {
	'/membre/clown_montmartre#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-50#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-100#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-150#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-200#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-250#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-300#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-350#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-400#ItemProduitsProposes': 'aventure',
	'/membre/clown_montmartre/o-450#ItemProduitsProposes': 'aventure',
}

class Command(BaseCommand):
    help = 'Imports Clown Montmartre pro'

    base_url = 'http://fr.zilok.com'

    thread_num = 1

    username = 'clownmont'

    # For Test
    #username = 'arclite'

    product_list_tag = {
		"name": "tbody",
		"attrs": {
			"id": "search_items"
		}
	}

    product_url_tag = {
    	"name": "a",
    }

    image_url_tag = {
    	"name": "img",
		"attrs": {
			"onclick": "return GB_showImageSet(image_set,1)"
            }
        }

    summary_tag = {
		"name": "h1",
		"attrs": {
			"class": "newcss_fiche-title"
		}
	}

    description_tag = {
		"name": "article",
		"attrs": {
			"class": "newcss_fiche-descr"
		}
	}

    price_tag = {
    	"name": "p",
    	"attrs": {
    		"class": "newcss_price"
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
                tmp_list = product_list_soup.find(self.product_list_tag["name"], self.product_list_tag["attrs"])
                product_list = tmp_list.find_all("tr")
                for product in product_list:
                	product_url = product.find(self.product_url_tag["name"]).get('href')
   	             	self.product_links[product_url] = family


    def _product_crawler(self):
    	from products.models import Product, Picture, Price

    	# Entry string : La caution peut etre laisser par carte bancaire (empreinte non debite), cheque ou bien en espece. Identifiant du produit : #383845
    	# Out string : La caution peut etre laisser par carte bancaire (empreinte non debite), cheque ou bien en espece. 
    	def remove_string_last_phrase(str, pattern):
    		return str.split(pattern, 1)[0]


    	# Entry ulr : //static.zilok.com/nas/media/ppbig/4223/422198.jpg
    	# Out url : static.zilok.com/nas/media/ppbig/4223/422198.jpg
    	def remove_img_url_double_slash(img_url):
    		return 'http://' + img_url[2:]
    	
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
				image_url = remove_img_url_double_slash(image_url)
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

			# Get the description
			try:
				description = product_soup.find(self.description_tag["name"], self.description_tag["attrs"]).text
				description = remove_string_last_phrase(description, "Identifiant du produit")
				#print "description : %s" % description
			except Exception, e:
				description = " "
				print 'pass description: %s' % str(e)
				pass

            # Get the price
			try:
				price = product_soup.find(self.price_tag["name"], self.price_tag["attrs"]).find('b').text
				#print 'price : %s' % price
			except Exception, e:
				print 'pass price: %s' % str(e)
				pass

			deposit_amount = 0.0

			from products.models import Category, Price
			from products.choices import UNIT
			print category_mapping[category]
			try:
				product = Product.objects.create(
					summary=summary, description=description, 
					deposit_amount=deposit_amount, address=self.address, owner=self.patron,
					category=Category.objects.get(slug=category_mapping[category])
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
        '/membre/clown_montmartre#ItemProduitsProposes',
        '/membre/clown_montmartre/o-50#ItemProduitsProposes',
		'/membre/clown_montmartre/o-100#ItemProduitsProposes',
		'/membre/clown_montmartre/o-150#ItemProduitsProposes',
		'/membre/clown_montmartre/o-200#ItemProduitsProposes',
		'/membre/clown_montmartre/o-250#ItemProduitsProposes',
		'/membre/clown_montmartre/o-300#ItemProduitsProposes',
		'/membre/clown_montmartre/o-350#ItemProduitsProposes',
		'/membre/clown_montmartre/o-400#ItemProduitsProposes',
		'/membre/clown_montmartre/o-450#ItemProduitsProposes',
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
