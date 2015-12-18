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
    '13-robes#/longueur-courte': 'robes-courtes',
    '13-robes#/longueur-longue': 'robes-longues',
    '25-bijoux': 'bijoux',
    '26-sacs': 'pochettes',
    '27-vestes': 'pochettes',
    '24-mariage': 'robes-de-mariage',
    '21-cocktail': 'robes-de-coktails',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'cestmarobe'"
    
    base_url = 'http://www.cestmarobe.com/fr/'
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
                product_list = product_list_soup.find_all('a', class_='product_img_link')
                for product in product_list:
                    product_url = product.get('href')
                    self.product_links[product_url] = family
                #print self.product_links


    
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

            #get the image
            try:
                image_url =  product_soup.find('div', id='big_img_scroll').find('img').get('src')
                #image_url = smart_urlquote(image_url)
                #print image_url
            except:
                print "pass image"
                pass

            # Get the title
            try:
                infosProduits = product_soup.find('img', id='bigpic').get('title')
                #print infosProduits
            except:
                infosProduits = ' '
                pass

            # Get the description
            try:
                description = product_soup.find('ul', class_='menu_accordeon').findAll('li')[-4].text
                #print description
            except:
                description = 'NO DESCRIPTION'
                pass

            # Format the title
            summary = infosProduits

            # Create deposit
            deposit_amount = 0.0

            # Add the price to the product
            try:
                price1 = product_soup.find('div', class_='price price_big').text
                price2 = (re.findall('\d+', price1 ))
                price = "%s.%s" % (int(price2[0]), int(price2[1]))
                #print price
            except:
                pass
            
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
                    print '\nerror loading image for object at url:', self.base_url + product_url

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
        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='cestmarobe')
            #user pas encore crée ... a modifier si ce n'est pas "cestmarobe"
        except Patron.DoesNotExist:
            print "Can't find user 'cestmarobe'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
            '13-robes#/longueur-courte',
            '13-robes#/longueur-longue',
            '25-bijoux'
            '26-sacs',
            '27-vestes',
            '24-mariage',
            '21-cocktail',
        ]
        #self._subpage_crawler()
        #self._product_crawler()
        
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