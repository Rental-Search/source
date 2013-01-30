# coding=utf-8
import re, sys, threading

from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError, quote
from contextlib import closing


category_mapping = {
	'Costume-Deguisement.asp?pid=7,1,120': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,6': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,121': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,15': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,149': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,7': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,14': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,2': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,9': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,13': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,17': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,4': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,11': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,20': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,1,19': 'pays-du-monde',
	'Costume-Deguisement.asp?pid=7,2,39': 'historique',
	'Costume-Deguisement.asp?pid=7,2,27': 'historique',
	'Costume-Deguisement.asp?pid=7,2,34': 'historique',
	'Costume-Deguisement.asp?pid=7,2,29': 'historique',
	'Costume-Deguisement.asp?pid=7,2,32': 'historique',
	'Costume-Deguisement.asp?pid=7,2,24': 'historique',
	'Costume-Deguisement.asp?pid=7,2,31': 'historique',
	'Costume-Deguisement.asp?pid=7,2,37': 'historique',
	'Costume-Deguisement.asp?pid=7,2,25': 'historique',
	'Costume-Deguisement.asp?pid=7,2,35': 'historique',
	'Costume-Deguisement.asp?pid=7,2,22': 'historique',
	'Costume-Deguisement.asp?pid=7,2,38': 'historique',
	'Costume-Deguisement.asp?pid=7,2,23': 'historique',
	'Costume-Deguisement.asp?pid=7,2,33': 'historique',
	'Costume-Deguisement.asp?pid=7,2,28': 'annees-60-70',
	'Costume-Deguisement.asp?pid=7,2,41': 'annees-60-70',
	'Costume-Deguisement.asp?pid=7,2,41': 'annees-60-70',
	'Costume-Deguisement.asp?pid=7,3,66': 'carnaval',
	'Costume-Deguisement.asp?pid=7,3,45': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,57': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,46': 'princesse',
	'Costume-Deguisement.asp?pid=7,3,58': 'carnaval',
	'Costume-Deguisement.asp?pid=7,3,69': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,61': 'carnaval',
	'Costume-Deguisement.asp?pid=7,3,70': 'aventure',
	'Costume-Deguisement.asp?pid=7,3,60': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,71': 'halloween',
	'Costume-Deguisement.asp?pid=7,3,59': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,73': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,51': 'pere-noel',
	'Costume-Deguisement.asp?pid=7,3,64': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,47': 'uniforme',
	'Costume-Deguisement.asp?pid=7,3,148': 'aventure',
	'Costume-Deguisement.asp?pid=7,3,65': 'aventure',
	'Costume-Deguisement.asp?pid=7,3,67': 'uniforme',
	'Costume-Deguisement.asp?pid=7,4,0': 'animal',
	'Costume-Deguisement.asp?pid=7,5,123': 'historique',
	'Costume-Deguisement.asp?pid=7,5,147': 'aventure',
	'Costume-Deguisement.asp?pid=7,5,124': 'perruque',
	'Costume-Deguisement.asp?pid=7,5,145': 'uniforme',
	'Costume-Deguisement.asp?pid=7,5,146': 'aventure',
	'Costume-Deguisement.asp?pid=7,5,144': 'masque',
	'Costume-Deguisement.asp?pid=7,5,122': 'pere-noel',
}

class Command(BaseCommand):
	args = ''
	help = 'Import pro site'

	base_url = 'http://www.sommier.com/'
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
			for product in product_list_soup.findAll(href=re.compile("img=")):
				product_url = product.get('href')
				self.product_links[product_url] = family_url


	def _product_crawler(self):
		"""Crawle product page and create a Product"""
		from eloue.products.models import Picture, Product, Category, Price, UNIT

		def _get_price(s):
			from decimal import Decimal as D
			return D(s[s.find("Prix de location : ")+18:s.find('\u20ac')].replace(' ', '').replace(',', '.'))

		def _get_summary(s):
			string = s[s.find("ref. :")+7:s.find(")")].lower()
			if string.startswith(u'z'):
				string = s[s.find(') ')+2:s.find(' (')]
			return 'costume %s' % string

		def _get_description(s):
			return 'Costume %s' % s[s.find(')')+2:s.find('Prix de location')].replace(': ',':\n - ').replace(', ', '\n - ')		

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

			product = product_soup.findAll(width='95%')[1]
			
			img_url = product.find('img').get('src')
			try:
				img_url = quote(img_url)
			except:
				img_url = None

			product_info = product.find('td', class_='collec').text
			summary = _get_summary(product_info)
			price = _get_price(product_info)
			description = _get_description(product_info)
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

			product.prices.add(Price(amount=price, unit=UNIT.DAY))
			sys.stdout.write('.')
			sys.stdout.flush()
	
	def handle(self, *args, **options):
		from eloue.accounts.models import Patron, Address
		self.product_links = {}

		try:
			self.patron = Patron.objects.get(pk=22860)
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




