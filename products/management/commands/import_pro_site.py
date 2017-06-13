# coding=utf-8
import re, sys, threading

from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError, quote
from contextlib import closing


category_mapping = {
	'-Chateaux-et-aires-de-jeux-.html': 'jeux-gonflables',
	'-Toboggans-Et-Multiplay-.html': 'jeux-gonflables',
	'-Gonflables-Sportifs-.html': 'jeux-gonflables',
	'-Gonflable-Animations-.html': 'jeux-gonflables',
	'-Gonflables-Pub-et-Deco-.html': 'jeux-gonflables',
	'-Pack-de-Jeux-Gonflables-.html': 'jeux-gonflables',
}


class Command(BaseCommand):
	args = ''
	help = 'Import pro site'

	base_url = 'http://www.asg34.com/'
	thread_num = 4

	def _subpage_crawler(self):
		"""Define the product links list"""
		while True:
			try: 
				family_url = self.product_families_url.pop()
			except IndexError:
				break

			with closing(urlopen(self.base_url + family_url)) as product_list_page:
				product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
				products = product_list_soup.find(id="conteneur")
			for product in products.findAll(class_="encadre"):
				product_url = product.find("a").get("href")
				self.product_links[product_url] = family_url

	def _product_crawler(self):
		"""Crawle product page and create a Product"""
		from products.models import Picture, Product, Category, Price
		from products.choices import UNIT

		def _get_price(s):
			from decimal import Decimal as D
			return D(s[s.find("Prix de location : ")+18:s.find('\u20ac')].replace(' ', '').replace(',', '.'))

		def _get_summary(s):
			return 'Structures gonflable : %s' % s

		def _get_description(s):
			string = s.find(class_="soustitre").get_text()

			string += u"\n\nCaractéristiques :\n\n"
			
			for li in s.findAll(class_="entry-content")[0].findAll("li"):
				string += "%s\n" % li.get_text()

			for paragraph in s.findAll(class_="entry-content")[0].findAll("p"):
				string += paragraph.get_text()

			return string

		while True:
			try:
				product_url, category = self.product_links.popitem()
			except KeyError:
				break
			
			try:
				with closing(urlopen(self.base_url + product_url)) as product_page:
					product_soup = BeautifulSoup(product_page, 'html.parser')
			except:
				print 'error loading page for object at url', self.base_url + product_url

			product = product_soup.find(id='ficheJeux')

			img_url = product.findAll("img")[0].get("src")
			try:
				img_url = quote(img_url)
			except:
				img_url = None

			summary = _get_summary(product.find("h1").string)

			description = _get_description(product)

			category = Category.objects.get(slug=category_mapping[category])

			product = Product.objects.create(summary=summary, description=description, 
   				deposit_amount=0, address=self.address, owner=self.patron,
   				category=category)

			if img_url:
				try:
					with closing(urlopen(self.base_url + img_url)) as image:
						product.pictures.add(Picture.objects.create(
							image=uploadedfile.SimpleUploadedFile(
	  							name='img', content=image.read())
	  						)
	  					)
				except HTTPError as e:
					print '\nerror loading image for object at url:', self.base_url + img_url

			sys.stdout.write('.')
			sys.stdout.flush()
	
	def handle(self, *args, **options):
		from accounts.models import Patron, Address
		self.product_links = {}

		try:
			self.patron = Patron.objects.get(pk=22981)
		except Patron.DoesNotExist:
			print "Can't find this patron"
			return

		self.address = self.patron.default_address or self.patron.addresses.all()[0]

		self.product_families_url = category_mapping.keys()

		for i in xrange(self.thread_num):
			threading.Thread(target=self._subpage_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()

		print 'Found %d object' % len(self.product_links)

		for i in xrange(self.thread_num):
			threading.Thread(target=self._product_crawler).start()
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()




