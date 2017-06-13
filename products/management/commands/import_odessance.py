# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile
from django.utils.html import smart_urlquote

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = {
'/location-robes-collection/attractive/':'robe',
'/location-robes-collection/bal-de-promo/':'robe',
'/location-robes-collection/bal-de-promo/page/2/':'robe',
'/location-robes-collection/collection-curves/':'robe',
'/location-robes-collection/collection-cortege/':'robe',
'/location-robes-collection/collection-nuptiale/':'robe',
'/location-robes-collection/collection-promesse/':'robe',
'/location-robes-collection/collection-starlight/':'robe',
'/location-robes-collection/collection-starlight/page/2/':'robe',
'/location-robes-collection/collection-starlight/page/3/':'robe',
'/location-robes-collection/collection-starlight/page/4/':'robe',
}


class Command(BaseCommand):
    help = "Imports given xls file for user 'fiestafolies'"
    
    base_url = 'http://odessance.fr/categorie-produit'

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break

   
            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('a', class_='product-main-link')
                for product in product_list:
                    product_url = product.get('href')
                    self.product_links[product_url] = family

    def _product_crawler(self):
        from products.models import Product, Picture, Price

        # Return the price in the right format
        def _to_decimal(s):
            from decimal import Decimal as D
            return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))   

        while True:
            try:
                product_url, category = self.product_links.popitem()
            except KeyError:
                break
            try:
                with closing(urlopen(product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', self.base_url + product_url

            #no need to parse all the page
            block = product_soup.find('div', id="content")

            # Get the title
            infosProduits = block.find('h1', class_="product_title entry-title").text

            # Get the description
            try:
                description = block.find('div', id='tab-description').find('p').text
            except:
                description = 'odessance'

            # Format the title
            summary = infosProduits

            deposit_amount = _to_decimal('0.0')

            details = block.find('div', class_="short-description").find('div', class_='std').text
            # description += '\n %s' % details

            # Create the product
            from products.models import Category, Price
            from products.choices import UNIT
            try:
                product = Product.objects.create(
                summary=summary, description=description, 
                deposit_amount=deposit_amount, address=self.address, owner=self.patron,
                category=Category.objects.get(slug=category_mapping[category]))
                try:
                    images = block.find('ul', class_="product_thumbnails").find_all('li') #this way we get all the four images
                    main_img = images[0].find('a').get('href')

                    with closing(urlopen(main_img)) as image:
                        product.pictures.add(Picture.objects.create(
                            image=uploadedfile.SimpleUploadedFile(
                                name='img', content=image.read())
                        )
                    )
                except HTTPError as e:
                    print '\nerror loading image for object at url:', self.base_url + product_url

                # Add the price to the product
                try:
                    regex = re.compile(r"(?<=Tarif location\W:\W)\d+")
                    price = regex.search(details)
                    price = _to_decimal(price.group(0))
                    product.prices.add(Price(amount=price, unit=UNIT.DAY))
                    sys.stdout.flush()
                except:
                    print 'ERROR PRICE'
                    pass
                print 'PRODUCT SUCCESSFULY CREATED'    
            except:
                print 'PRODUCT CANNOT BE CREATED'
                pass


    def handle(self, *args, **options):

        if len(args) > 1:
            print '2 arguments given, expected one ...'
            return
        try:
            thread_num = int(args[0])
        except:
            thread_num = 2

        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='odessance')
        except Patron.DoesNotExist:
            print "Can't find user 'odessance'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

    #     # Get families list of products
        self.product_families = [
        '/location-robes-collection/attractive/',
        '/location-robes-collection/bal-de-promo/',
        '/location-robes-collection/bal-de-promo/page/2/',
        '/location-robes-collection/collection-curves/',
        '/location-robes-collection/collection-cortege/',
        '/location-robes-collection/collection-nuptiale/',
        '/location-robes-collection/collection-promesse/',
        '/location-robes-collection/collection-starlight/',
        '/location-robes-collection/collection-starlight/page/2/',
        '/location-robes-collection/collection-starlight/page/3/',
        '/location-robes-collection/collection-starlight/page/4/',
         ]
    #     # self.product_families = self.soup.findAll('a', href=re.compile('famille'))
        
        # List the products
        for i in xrange(thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

        print 'Found %d object' % len(self.product_links)

        # Create the products in the database
        for i in xrange(thread_num):
            threading.Thread(target=self._product_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()