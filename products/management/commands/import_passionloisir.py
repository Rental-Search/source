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
'/structures-gonflables/location-structures-sportives/':'jeux-gonflables',
'/structures-gonflables/location-structures-sportives/2/':'jeux-gonflables',
'/structures-gonflables/structure-gonflable-de-3-ans-a-10-ans/':'jeux-gonflables',
'/structures-gonflables/structure-gonflable-de-3-ans-a-10-ans/2/':'jeux-gonflables',
'/structures-gonflables/nouveautes/':'jeux-gonflables',
'/location-sumos/':'jeux-gonflables',
'/location-taureau-mecanique/':'jeux-dadresse',
'/location-jeux-de-cafe/flippers-en-location/':'jeux-de-bistrot',
'/location-jeux-de-cafe/flippers-en-location/2/':'jeux-de-bistrot',
'/location-jeux-de-cafe/flippers-en-location/3/':'jeux-de-bistrot',
'/location-jeux-de-cafe/location-baby-foot-stella/':'jeux-de-bistrot',
'/location-jeux-de-cafe/location-borne-flechette/':'jeux-de-bistrot',
'/location-jeux-de-cafe/location-borne-arcade-1/':'jeux-de-bistrot',
'/location-jeux-de-cafe/location-billard-semi-pro/':'jeux-de-bistrot',
'/location-jeux-de-cafe/location-air-hockey/':'jeux-de-bistrot',
'/location-baby-foot-xl-stella/':'jeux-de-bistrot',
# '/location-jeux-d-estaminets/':'jeux-de-bistrot',
# '/mariage/':'',
'/location-chapiteaux/':'chapiteau',
'/location-materiel-video/location-borne-tactile-32/':'jeux-de-bistrot',
'/location-materiel-restauration/':'ustensiles-de-table',
'/location-jeux-de-casino/':'jeux-de-bistrot',
'/mobilier/':'meuble',
'/location-materiel-video/':'videoprojecteur',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'DEGUIZLAND'"
    
    base_url = 'http://www.passionloisir.com/album'

    total = 0
    price_found = 0

    def _subpage_crawler(self):
        from products.models import Product, Picture, Price
        """Create the list of products by finding the link of each product page"""

        def _to_decimal(s):
            from decimal import Decimal as D
            return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))

        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break

            # print self.base_url + family
            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                if product_list_soup.find('ul', id='photogallery_listlarge_items'):
                    product_list = product_list_soup.find('ul', id='photogallery_listlarge_items').findAll('li')
                    # print 'Found %d object' % len(product_list)
                    self.total += len(product_list)
                    for product in product_list:
                        infosProduits = product.find('dt', class_="item_title").find('a').get('title')

                        image_url = product.find('a').get('href')

                        try:
                            product.find('dd')
                            description = product.find('dd').text
                            # print description
                        except:
                            description = ''
                        
                        # long way to go to get the price...
                        try:
                            price = re.search(u'[0-9]+(\.[0-9]+)?\s?\u20AC', description)
                            price = price.group(0)
                            price = _to_decimal(price)
                            self.price_found += 1
                        except:
                            try:
                                price = re.search(u'[0-9]+(\.[0-9]+)?\s?\u20AC', infosProduits)
                                price = price.group(0)
                                price = _to_decimal(price)
                                self.price_found += 1
                            except:
                                pass
                            pass
                        
                        summary = infosProduits
                        deposit_amount = 0.0

                        # Create the product
                        from products.models import Category, Price
                        from products.choices import UNIT
                        try:
                            product = Product.objects.create(
                                summary=summary, description=description, 
                                deposit_amount=deposit_amount, address=self.address, owner=self.patron,
                                category=Category.objects.get(slug=category_mapping[family]))

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
                            try:
                                price = _to_decimal(description)
                                product.prices.add(Price(amount=price, unit=UNIT.DAY))
                                sys.stdout.flush()
                            except:
                                print 'PRICE ERROR'
                                pass
                        except:
                            print 'CANNOT CREATE THE PRODUCT'
                            pass

    def handle(self, *args, **options):
        if len(args) > 1:
            print '2 arguments given, expected one ...'
            return
        try:
            thread_num = int(args[0])
            print type(thread_num)
        except:
            thread_num = 2

        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='Passionloisir')
        except Patron.DoesNotExist:
            print "Can't find user 'Passionloisir'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
        '/structures-gonflables/location-structures-sportives/',
        '/structures-gonflables/location-structures-sportives/2/',
        '/structures-gonflables/structure-gonflable-de-3-ans-a-10-ans/',
        '/structures-gonflables/structure-gonflable-de-3-ans-a-10-ans/2/',
        '/structures-gonflables/nouveautes/',
        '/location-sumos/',
        '/location-taureau-mecanique/',
        '/location-jeux-de-cafe/flippers-en-location/',
        '/location-jeux-de-cafe/flippers-en-location/2/',
        '/location-jeux-de-cafe/flippers-en-location/3/',
        '/location-jeux-de-cafe/location-baby-foot-stella/',
        '/location-jeux-de-cafe/location-borne-flechette/',
        '/location-jeux-de-cafe/location-borne-arcade-1/',
        '/location-jeux-de-cafe/location-billard-semi-pro/',
        '/location-jeux-de-cafe/location-air-hockey/',
        '/location-baby-foot-xl-stella/',
        # '/location-jeux-d-estaminets/':'jeux-de-bistrot',
        # '/mariage/':'',
        '/location-chapiteaux/',
        '/location-materiel-video/location-borne-tactile-32/',
        '/location-materiel-restauration/',
        '/location-jeux-de-casino/',
        '/mobilier/',
        '/location-materiel-video/',
         ]
        # self.product_families = self.soup.findAll('a', href=re.compile('famille'))
        
        # List the products
        for i in xrange(thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()
        print '\n\nTOTAL NB OF PRODUCTS = %s' % self.total    
        print '\n NB OF PRICES = %s' % self.price_found