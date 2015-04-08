# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '/effetdisco1/': 'jeu-de-lumiere',
    '/effetdiscoleds/': 'jeu-de-lumiere',
    '/effetsdivers/':'jeu-de-lumiere',
    '/projecteur/':'projecteur',
    '/laserstroboscope/':'jeu-de-lumiere',
    '/bouleafacettes/':'jeu-de-lumiere',
    '/machine/':'machine-neige',
    '/structurespieds/':'equipement-dj',
    '/controleslumiere/':'jeu-de-lumiere',
    '/amplification/':'amplificateur',
    '/enceintes/':'enceinte-dj',
    '/tabledemixage/':'equipement-dj',
    '/platinedj/':'equipement-dj',
    '/micro/':'micro-filaire',
    '/casques/':'casques-dj',
    '/peripherique/':'equipement-dj',
    '/videoprojecteur/':'projecteur',
    '/ecranblancprojection/':'projecteur',
    '/sonoconference/': 'enceinte-dj',
    '/effetsspeciaux/':'jeu-de-lumiere',
    '/packsono1/':'enceinte-dj',
    '/packdjmix/':'equipement-dj',
    }


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'DEGUIZLAND'"
    
    base_url = 'http://www.scherloc.com'

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break    

            with closing(urlopen(self.base_url + family + 'index.html')) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('table',class_='wg-paragraph')
                for product in product_list:
                    if product.find('tr').find('td').find('a', href=re.compile('page')):
                        product_url = self.base_url + family + product.find('tr').find('td').find('a', href=re.compile('page')).get('href')
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
                # print product_url
            except KeyError:
                break    
            try:
                with closing(urlopen(product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', self.base_url + product_url


            family = product_url.split('/')[3]
            # Get the image
            try:
                image_url = product_soup.find('a', href=re.compile('.+\.jpg')).get('href')
                image_url = product_url.rsplit('/', 1)[0] + '/' + image_url
            except:
                pass

            # Get the title
            try:
                infosProduits = product_soup.find('h2').text
            except:
                infosProduits = ''
            # print infosProduits

            # Get the price
            # price_soup = product_soup.find('span', attrs={'class': 'wg-price'})
            # print price_soup
            # print price


            # Get the description
            try:
                description = product_soup.find('td', style='text-align:justify').text
            except:
                print 'no description'
                pass


            # Format the title
            summary = infosProduits

            deposit_amount = 0.0

            # print 'summary : %s\n description : %s\n' % (summary, description)

            # Create the product
            try:
                from products.models import Category, Price
                from products.choices import UNIT
                product = Product.objects.create(
                    summary=summary, description=description, 
                    deposit_amount=deposit_amount, address=self.address, owner=self.patron,
                    category=Category.objects.get(slug=category_mapping[category]))
                try:
                    with closing(urlopen(image_url)) as image:
                        product.pictures.add(Picture.objects.create(
                            image=uploadedfile.SimpleUploadedFile(
                                name='img', content=image.read())
                        )
                    )
                except HTTPError as e:
                    print '\nerror loading image for object at url:', self.base_url + product_url
            except:
                print 'CANNOT CREATE PRODUCT : %s' % summary
                pass
            
    #         # # Add the price to the product
    #         # product.prices.add(Price(amount=price, unit=UNIT.DAY))
    #         # sys.stdout.write('.')
    #         # sys.stdout.flush()


    def handle(self, *args, **options):
        if len(args) > 1:
            print '2 arguments given, expected one ...'
            return
        try:
            thread_num = int(args[0])
            print type(thread_num)
        except:
            thread_num = 4

        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='scherloc')
        except Patron.DoesNotExist:
            print "Can't find user 'scherloc'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
        '/effetdisco1/',
        '/effetdiscoleds/',
        '/effetsdivers/',
        '/projecteur/',
        '/laserstroboscope/',
        '/bouleafacettes/',
        '/machine/',
        '/structurespieds/',
        '/controleslumiere/',
        '/amplification/',
        '/enceintes/',
        '/tabledemixage/',
        '/platinedj/',
        '/micro/',
        '/casques/',
        '/peripherique/',
        '/videoprojecteur/',
        '/ecranblancprojection/',
        '/sonoconference/',
        '/effetsspeciaux/',
        '/packsono1/',
        '/packdjmix/',
        ]
        # self.product_families = self.soup.findAll('a', href=re.compile('famille'))
        
        # List the products
        for i in xrange(thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

        print 'Found %d object' % len(self.product_links)

        # # Create the products in the database
        for i in xrange(thread_num):
            threading.Thread(target=self._product_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()