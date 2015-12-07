# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    'cat-prod.php?cat_id=5&g_id=11&gamme_id=11':'amplificateur',
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
                print self.product_links

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
                image_url = product_soup.find('a', class_="MagicZoomPlus").find('img').get('src')
                #print "image_url : %s" % image_url
            except:
                print "pass image"
                pass

        #     #Get the title
        #     try:
        #         summary = product_soup.find('h1').text
        #         #print "summary : %s" % summary
        #     except:
        #         print "pass title"
        #         pass
            
        #     # Get the description
        #     try:
        #         description1 = product_soup.find('div', id='short_description_content').find('p').text
        #         description2 = product_soup.find('div', id='more_info_sheets').find('p').text
        #         description3 = product_soup.find('div', id='more_info_sheets').find_all('span', style="box-sizing: border-box; font-size: 12.222222328186px;")
        #         description4 = "\n".join([description.text for description in description3])
        #         description = "%s\n%s\n%s" % (description1, description2, description4)
        #         #print "description : %s" % description
        #     except:
        #         description = " "
        #         print 'pass description'
        #         pass

        #     # Get the price
        #     try:
        #         price1 = product_soup.find('span', id='our_price_display').text
        #         price2 = (re.findall('\d+', price1 ))
        #         price = "%s.%s" % (int(price2[0]), int(price2[1]))
        #         #print "price : %s" % price
        #     except:
        #         price = "10.00"
        #         print 'pass price'
        #         pass

        #     # Create deposit
        #     deposit_amount = 0.0

        #     # Create the product
        #     from products.models import Category, Price
        #     from products.choices import UNIT
        #     try:
        #         #print "try create"
        #         product = Product.objects.create(
        #             summary=summary, description=description, 
        #             deposit_amount=deposit_amount, address=self.address, owner=self.patron,
        #             category=Category.objects.get(slug=category_mapping[category])
        #         )
        #         #print "product_id : %s" % product.pk

        #         try:
        #             #print "try upload image"
        #             with closing(urlopen(image_url)) as image:
        #                 product.pictures.add(Picture.objects.create(
        #                     image=uploadedfile.SimpleUploadedFile(
        #                         name='img', content=image.read())
        #                 )
        #             )
        #             #print "picture : %s" % product.pictures.all()[0]
        #         except HTTPError as e:
        #             print '\nerror loading image for object at url:', self.base_url + product_url

        #         # Add the price to the product
        #         try:
        #             product.prices.add(Price(amount=price, unit=UNIT.DAY))
        #             #print "price : %s" % product.prices.all()[0]
        #         except:
        #             print 'PRICE ERROR'
        #             pass

        #         # sys.stdout.write('.')
        #         # sys.stdout.flush()
        #     except:
        #         print 'CANNOT CREATE THE PRODUCT %s \n %s' % (summary, product_url)
        #         pass

        # print "\n %s products created" % self.patron.products.all().count()
 

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
            self.patron = Patron.objects.get(username='hugow') #rslocation18 aussi ?
        except Patron.DoesNotExist:
            print "Can't find user 'sabannes-reception'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Get families list of products
        self.product_families = [
        'cat-prod.php?cat_id=5&g_id=11&gamme_id=11',

        ]

        self._subpage_crawler()
        self._product_crawler()

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

