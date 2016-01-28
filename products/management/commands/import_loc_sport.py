# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '/particuliers/activités-sportives-ludiques/nature-dextérité-1/':'jeux-dadresse',

}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'hwoog'"
    
    base_url = 'http://www.locsport64.fr'
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
                product_list = product_list_soup.find_all('div',class_='product-container')
                for product in product_list:
                    product_url = product.find('a').get('href')
                    self.product_links[product_url] = family
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
                image_url = product_soup.find('img', id="bigpic").get('src')
                #print "image_url : %s" % image_url
            except:
                print "pass image"
                pass

            #Get the title
            try:
                summary = product_soup.find('h1').text
                #print "summary : %s" % summary
            except:
                print "pass title"
                pass
            
            # Get the description
            try:
                description = product_soup.find('div', id='short_description_content').text
                #print "description : %s" % description
            except:
                description = " "
                print 'pass description'
                pass

            # Get the price
            try:
                price = product_soup.find('div', class_='price').find('span').text
                price = _to_decimal(price)
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
            self.patron = Patron.objects.get(username='locationevents')
        except Patron.DoesNotExist:
            print "Can't find user 'Event-location locationevents'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Get families list of products
        self.product_families = [
        '/particuliers/activités-sportives-ludiques/nature-dextérité-1/',

        ]
        self._subpage_crawler()
        #self._product_crawler()

        # #List the products and create the product in the database
        # for i in xrange(self.thread_num):
        #     threading.Thread(target=self._subpage_crawler).start()
        # for thread in threading.enumerate():
        #     if thread is not threading.currentThread():
        #         thread.join()

        # print 'Found %d objects' % len(self.product_links)

        # #Create the products in the database
        # for i in xrange(self.thread_num):
        #     threading.Thread(target=self._product_crawler).start()
        # for thread in threading.enumerate():
        #     if thread is not threading.currentThread():
        #         thread.join()

