# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    'cat-prod.php?cat_id=5&g_id=11&gamme_id=11':'tables-et-buffets',
    'cat-prod.php?cat_id=5&g_id=10&gamme_id=10':'chaises',
    'cat-prod.php?cat_id=5&g_id=12&gamme_id=12':'mobilier-de-jardin',
    'cat-prod.php?cat_id=5&g_id=55&gamme_id=55':'meuble',
    'cat-prod.php?cat_id=5&g_id=57&gamme_id=57':'meuble',

    'cat-prod.php?cat_id=6&g_id=13&gamme_id=13':'decoration',
    'cat-prod.php?cat_id=6&g_id=14&gamme_id=14':'decoration',
    'cat-prod.php?cat_id=5&g_id=15&gamme_id=15':'decoration',
    'cat-prod.php?cat_id=5&g_id=16&gamme_id=16':'decoration',
    'cat-prod.php?cat_id=5&g_id=35&gamme_id=35':'jeu-de-lumiere',
    'cat-prod.php?cat_id=5&g_id=36&gamme_id=36':'jeu-de-lumiere',
    'cat-prod.php?cat_id=5&g_id=38&gamme_id=38':'mobilier-de-jardin',
    'cat-prod.php?cat_id=5&g_id=50&gamme_id=50':'decoration',

    'cat-prod.php?cat_id=5&g_id=63&gamme_id=63':'decoration',
    'cat-prod.php?cat_id=5&g_id=18&gamme_id=18':'barbecue',
    'cat-prod.php?cat_id=5&g_id=21&gamme_id=21':'couverts',
    'cat-prod.php?cat_id=5&g_id=54&gamme_id=54':'decoration',
    'cat-prod.php?cat_id=5&g_id=64&gamme_id=64':'decoration',

    'cat-prod.php?cat_id=5&g_id=22&gamme_id=22':'connectique',
    'cat-prod.php?cat_id=5&g_id=23&gamme_id=23':'spot',
    'cat-prod.php?cat_id=5&g_id=24&gamme_id=24':'accessoires-tv',
    'cat-prod.php?cat_id=5&g_id=25&gamme_id=25':'connectique',
    'cat-prod.php?cat_id=5&g_id=26&gamme_id=26':'structures',
    'cat-prod.php?cat_id=5&g_id=27&gamme_id=27':'gradin-estrade-podium',
    'cat-prod.php?cat_id=5&g_id=48&gamme_id=48':'connectique',

    'cat-prod.php?cat_id=5&g_id=29&gamme_id=29':'decoration',

    'cat-sgamme.php?sg_id=28&g_id=16&cat_id=6':'tente-de-reception',
    'cat-sgamme.php?sg_id=29&g_id=16&cat_id=6':'structures',
    'cat-sgamme.php?sg_id=30&g_id=16&cat_id=6':'chauffage',
    'cat-sgamme.php?sg_id=114&g_id=16&cat_id=6':'groupe-electrogene',
    'cat-sgamme.php?sg_id=115&g_id=16&cat_id=6':'travaux',
    'cat-sgamme.php?sg_id=116&g_id=16&cat_id=6':'structures',
    'cat-prod.php?cat_id=10&g_id=31&gamme_id=31':'jeux-de-societe',
    'cat-prod.php?cat_id=16&g_id=40&gamme_id=40':'chaises',
    'cat-prod.php?cat_id=16&g_id=65&gamme_id=65':'chaises',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'hugow'"
    
    base_url = 'http://www.sabannes-reception.com/'
    thread_num = 1

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                #print "ERREUR DE LINDEX"
                break
            
            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('div', class_="item-image-container")
                for product in product_list:
                    product_url = product.find('a').get('href')
                    self.product_links[self.base_url + product_url] = family
                #print self.product_links

    def _product_crawler(self):
        from products.models import Product, Picture, Price

        # Return the price in the right format
        def _to_decimal(s):
            from decimal import Decimal as D
            return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))   

        #print self.product_links

        while True:
            try:  
                product_url, category = self.product_links.popitem()
            except KeyError:
                break

            #print product_url 
            #product_url = quote(product_url)
            try:
                with closing(urlopen(product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', product_url


            #Get the image
            try:
                image_url1 = product_soup.find('div', id="product-image-container").find('img').get('src').replace(" ", "%20")
                image_url = self.base_url + image_url1
                #print "image_url : %s" % image_url
            except:
                print "pass image"
                pass

            #Get the title
            try:
                summary = product_soup.find('h1', class_="product-name").text
                #print "summary : %s" % summary
            except:
                print "pass title"
                pass
            
            # Get the description
            try:
                description1 = product_soup.find('div', id='overview').text
                description2 = product_soup.find('div', id='review').text
                description3 = product_soup.find('div', id='utilisation').text
                description = "%s\n%s\n%s" % (description1, description2, description3)
                #print "description : %s" % description
            except:
                description = " "
                print 'pass description'
                pass

            # Get the price
            try:
                price1 = product_soup.find('span', class_="item-price").text
                price2 = (re.findall('\d+', price1 ))
                price = "%s.%s" % (int(price2[2]), int(price2[3]))
                #print "price : %s" % price
            except:
                price = "10.00"
                print 'pass price'
                pass

            # Create deposit
            deposit_amount = 0.0

            # Create the product
            from products.models import Category, Price
            from products.choices import UNIT
            try:
                #print "try create"
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
                    print '\nerror loading image for object at url: %s' % product_url

                # Add the price to the product
                try:
                    product.prices.add(Price(amount=price, unit=UNIT.DAY))
                    #print "price : %s" % product.prices.all()[0]
                except:
                    print 'PRICE ERROR'
                    pass

                # sys.stdout.write('.')
                # sys.stdout.flush()
            except:
                print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
                pass

        print "\n %s products created" % self.patron.products.all().count()
 

    def handle(self, *args, **options):
        if len(args) > 1:
            print '2 arguments given, expected one ...'
            return
        try:
            thread_num = int(args[0])
            print type(thread_num)
        except:
            thread_num = 1

        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='sabannesreception') #rslocation18 aussi ?
        except Patron.DoesNotExist:
            print "Can't find user 'sabannesreception'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Get families list of products
        self.product_families = [
        'cat-prod.php?cat_id=5&g_id=11&gamme_id=11',
        'cat-prod.php?cat_id=5&g_id=10&gamme_id=10',
        'cat-prod.php?cat_id=5&g_id=12&gamme_id=12',
        'cat-prod.php?cat_id=5&g_id=55&gamme_id=55',
        'cat-prod.php?cat_id=5&g_id=57&gamme_id=57',

        'cat-prod.php?cat_id=6&g_id=13&gamme_id=13',
        'cat-prod.php?cat_id=6&g_id=14&gamme_id=14',
        'cat-prod.php?cat_id=5&g_id=15&gamme_id=15',
        'cat-prod.php?cat_id=5&g_id=16&gamme_id=16',
        'cat-prod.php?cat_id=5&g_id=35&gamme_id=35',
        'cat-prod.php?cat_id=5&g_id=36&gamme_id=36',
        'cat-prod.php?cat_id=5&g_id=38&gamme_id=38',
        'cat-prod.php?cat_id=5&g_id=50&gamme_id=50',

        'cat-prod.php?cat_id=5&g_id=63&gamme_id=63',
        'cat-prod.php?cat_id=5&g_id=18&gamme_id=18',
        'cat-prod.php?cat_id=5&g_id=21&gamme_id=21',
        'cat-prod.php?cat_id=5&g_id=54&gamme_id=54',
        'cat-prod.php?cat_id=5&g_id=64&gamme_id=64',

        'cat-prod.php?cat_id=5&g_id=22&gamme_id=22',
        'cat-prod.php?cat_id=5&g_id=23&gamme_id=23'
        'cat-prod.php?cat_id=5&g_id=24&gamme_id=24',
        'cat-prod.php?cat_id=5&g_id=25&gamme_id=25',
        'cat-prod.php?cat_id=5&g_id=26&gamme_id=26',
        'cat-prod.php?cat_id=5&g_id=27&gamme_id=27',
        'cat-prod.php?cat_id=5&g_id=48&gamme_id=48',

        'cat-prod.php?cat_id=5&g_id=29&gamme_id=29',

        'cat-sgamme.php?sg_id=28&g_id=16&cat_id=6',
        'cat-sgamme.php?sg_id=29&g_id=16&cat_id=6',
        'cat-sgamme.php?sg_id=30&g_id=16&cat_id=6',
        'cat-sgamme.php?sg_id=114&g_id=16&cat_id=6',
        'cat-sgamme.php?sg_id=115&g_id=16&cat_id=6',
        'cat-sgamme.php?sg_id=116&g_id=16&cat_id=6',
        'cat-prod.php?cat_id=10&g_id=31&gamme_id=31',
        'cat-prod.php?cat_id=16&g_id=40&gamme_id=40',
        'cat-prod.php?cat_id=16&g_id=65&gamme_id=65',
        ]

        # self._subpage_crawler()
        # self._product_crawler()

        #List the products and create the product in the database
        for i in xrange(self.thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

        print 'Found %d objects' % len(self.product_links)

        #Create the products in the database
        for i in xrange(self.thread_num):
            threading.Thread(target=self._product_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

