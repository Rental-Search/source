# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing


category_mapping = {
	'/manutention/chariot-elevateur.html': 'travaux',
	'/manutention/chariot-elevateur/page2.html': 'travaux',
	'/manutention/chariot-elevateur/page3.html': 'travaux',
	'/manutention/materiel-de-magasinage.html': 'travaux',
	'/manutention/materiel-de-magasinage/page2.html': 'travaux',
	'/manutention/materiel-de-magasinage/page3.html': 'travaux',
	'/manutention/materiel-de-magasinage/page4.html': 'travaux',
	'/manutention/nacelle.html': 'travaux',
	'/manutention/nacelle/page2.html': 'travaux',
	'/manutention/nacelle/page3.html': 'travaux',
	'/manutention/nacelle/page4.html': 'travaux',
	'/manutention/nettoyage-industriel.html': 'travaux',
	'/manutention/nettoyage-industriel/page2.html': 'travaux'
}


class Command(BaseCommand):
	args = ''
	help = "Imports aprolis pro"

	base_url = 'http://www.aprolis.com'
	thread_num = 1

	username='Aprolis'

	product_list_tag = {
		"name": "div",
		"attrs": {
			"class": "product"
		}
	}

	product_url_tag = {
		"name": "a",
		"attrs": {
			"class": "titleProduct"
		}
	}

	image_url_tag = {
		"name": "img",
		"attrs": {
			"class": "visuelPrincipal"
		}
	}

	summary_tag = {
		"name": "h1",
		"attrs": ""
	}

	description_tag = {
		"name": "div",
		"attrs": {
			"class": "details"
		}
	}

	price_tag = None


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
					product_url = product.find(self.product_url_tag["name"], self.product_url_tag["attrs"]).get('href')
					self.product_links[self.base_url + product_url] = family

	def _product_crawler(self):
		from products.models import Product, Picture, Price

        # Return the price in the right format
		def _to_decimal(s):
			from decimal import Decimal as D
			return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))

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
				image_url = self.base_url + product_soup.find(self.image_url_tag["name"], self.image_url_tag["attrs"]).get('src')
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
				description = product_soup.find(self.description_tag["name"], self.description_tag["attrs"]).find("p").text
			except Exception, e:
				description = " "
				#print 'pass description: %s' % str(e)
				pass

            # Get the price
			if self.price_tag:
				try:
					price = product_soup.find('span', class_='amount').find('span').text
					price = _to_decimal(price)
				except:
					print 'pass price'
					pass

			# Create deposit
			deposit_amount = 0.0

			# Create the product
			from products.models import Category, Price
			from products.choices import UNIT
			try:
				product = Product.objects.create(
					summary=summary, description=description, 
					deposit_amount=deposit_amount, address=self.address, owner=self.patron,
					category=Category.objects.get(slug=category_mapping[category])
				)
                #print "product_id : %s" % product.pk

				try:
					#print "try upload image"
					with closing(urlopen(image_url)) as image:
						product.pictures.add(Picture.objects.create(
							image=uploadedfile.SimpleUploadedFile(
							name='img', content=image.read())
						)
					)
					#print "picture : %s" % product.pictures.all()[0]
				except HTTPError as e:
					print '\nerror loading image for object at url:', self.base_url + product_url

				# Add the price to the product
				if self.price_tag:
					try:
						if price:
							product.prices.add(Price(amount=price, unit=UNIT.DAY))
						#print "price : %s" % product.prices.all()[0]
					except Exception, e:
						print 'PRICE ERROR'
						pass

                # sys.stdout.write('.')
                # sys.stdout.flush()
			except Exception, e:
				print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
				print 'error: %s' % str(e)
				pass

		print "\n %s products created" % self.patron.products.all().count()



	def handle(self, *args, **options):
		from accounts.models import Patron, Address
		self.product_links = {}

		# Get the user
		try:
			self.patron = Patron.objects.get(username=self.username)
		except Patron.DoesNotExist:
			print "Can't find user 'aprolis'"
			return

		# Get the default address of the user to add to the product
		self.address = self.patron.default_address or self.patron.addresses.all()[0]

		# Get families list of products
		self.product_families = [
			'/manutention/chariot-elevateur.html',
			'/manutention/chariot-elevateur/page2.html',
			'/manutention/chariot-elevateur/page3.html',
			'/manutention/materiel-de-magasinage.html',
			'/manutention/materiel-de-magasinage/page2.html',
			'/manutention/materiel-de-magasinage/page3.html',
			'/manutention/materiel-de-magasinage/page4.html',
			'/manutention/nacelle.html',
			'/manutention/nacelle/page2.html',
			'/manutention/nacelle/page3.html',
			'/manutention/nacelle/page4.html',
			'/manutention/nettoyage-industriel.html',
			'/manutention/nettoyage-industriel/page2.html'
		]
        
        # List the products
		for i in xrange(self.thread_num):
			threading.Thread(target=self._subpage_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()

		print 'Found %d objects' % len(self.product_links)

		# Create the products in the database
		for i in xrange(self.thread_num):
			threading.Thread(target=self._product_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()