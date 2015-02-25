# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing
from django.utils.encoding import smart_str

category_mapping = { 
    'http://1robepour1soir.com/robes/': 'robe',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'DEGUIZLAND'"
    
    base_url = 'http://1robepour1soir.com'
    thread_num = 1

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break

            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('div', id=re.compile('post-[0-9]*'))
                for product in product_list:
                    product_url = product.find('a').get('href')
                    self.product_links[product_url] = self.base_url + family
    
    def _product_crawler(self):
        from products.models import Product, Picture, Price

        # Return the price in the right format
        def _to_decimal(s):
            from decimal import Decimal as D
            return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))

        while True:
            try:
                product_url, category_slug = self.product_links.popitem()
            except KeyError:
                break

            try:
                with closing(urlopen(product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', self.base_url + product_url

            # Get the image
            if product_soup.find('div', class_="szg-thumbs"):
                image_url =  product_soup.find('div', class_="szg-thumbs").find('img').get('data-medium')

            # Get the title
            infosProduits = product_soup.find('h2', class_='supertitre').text

            # Get the price
            try:
                price_str = product_soup.find('div', class_='prix').find('p').text
                price = _to_decimal(price_str)
            except:
                pass

            # Get the description
            description = product_soup.find('div', id='tab1').text
            description = re.sub(r"\s{2,}","",description).strip()

            #Format the title
            summary = infosProduits

            if price:
                print '%s\n%s\n%s\n%s' % (product_url, price, description, summary)
            else:
                print '%s\n%s\n%s' % (product_url, description, summary)
            
            # Create the product
            from products.models import Category, Price
            from products.choices import UNIT
            product = Product.objects.create(
                summary=summary, description=description, 
                deposit_amount=0.0, address=self.address, owner=self.patron,
                category=Category.objects.get(slug=category_mapping[category_slug]))
            try:
                with closing(urlopen(image_url)) as image:
                    product.pictures.add(Picture.objects.create(
                        image=uploadedfile.SimpleUploadedFile(
                            name='img', content=image.read())
                    )
                )
            except HTTPError as e:
                print '\nerror loading image for object at url:', self.base_url + product_url
            
            # Add the price to the product
            if price:
              product.prices.add(Price(amount=price, unit=UNIT.DAY))
            # sys.stdout.write('.')
            # sys.stdout.flush()


    def handle(self, *args, **options):
        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='LOXAM')
        except Patron.DoesNotExist:
            print "Can't find user 'deguizeland'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = ['/robes/']
        
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