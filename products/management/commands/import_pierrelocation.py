# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '/transport-manutention/':'travaux',
    '/travail-en-hauteur/':'echafaudage',
    '/chauffage/':'chauffage',
    '/gros-oeuvre/':'pelle-pioche-et-tariere',
    '/second-oeuvre/outillage-pneumatique/':'compresseur',
    '/second-oeuvre/perforateur-burineur-piqueur-brise-béton/':'marteau-piqueur',
    '/second-oeuvre/scie-découpeuse-carotteuse-meuleuse/':'scie-circulaire',
    '/second-oeuvre/ponçage-du-sol/':'ponceuse',
    '/second-oeuvre/rénovation-sol-et-mur/':'decolleuse',
    '/second-oeuvre/perceuse-boulonneuse/':'perceuse-sans-fil',
    '/second-oeuvre/ponçage/':'ponceuse',
    '/second-oeuvre/travail-du-bois/':'rabot-electrique',
    '/second-oeuvre/peinture-laque-crépi/':'pistolet-a-peinture',
    '/second-oeuvre/soudure/':'soudure-et-plomberie',
    '/second-oeuvre/divers/':'travaux',
    '/nettoyage/':'aspirateur-industriel',
    '/espaces-verts/':'tondeuse-et-autoporte',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'PierreAndreLocation'"
    
    base_url = 'http://www.pierrelocation.fr/location'

    def _subpage_crawler(self):
        from products.models import Product, Picture, Price

        # Return the price in the right format
        def _to_decimal(s):
            from decimal import Decimal as D
            return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))

        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
                category = family
            except IndexError:
                break

            try:
                with closing(urlopen(self.base_url + family)) as product_list_page:
                    product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                    product_list = product_list_soup.find_all('div', class_='product-presentation product-presentation-1')

                    for product_soup in product_list:
                        image_url = product_soup.find('a', class_="showOriginalImage active").get('href')
                        # print image_url

                        #Get the title
                        infosProduits = product_soup.find('div', class_='name').text
                        # print infosProduits

                        # Get the price
                        price = product_soup.find('div', class_='price').text
                        price = _to_decimal(price)

                        #Get the deposit ammount
                        deposit_amount = 0.0

                        # Get the description
                        description = ""
                        description_soup = product_soup.find('div', class_='description')
                        for p in description_soup.find_all('p'):
                            if p.text != 'LOCATION':
                                description += '%s \n' % p.text
                        # print description

                        #summary
                        summary = infosProduits


                        # Create the product
                        from products.models import Category, Price
                        from products.choices import UNIT
                        try:
                            product = Product.objects.create(
                            summary=summary, description=description, 
                            deposit_amount=deposit_amount, address=self.address, owner=self.patron,
                            category=Category.objects.get(slug=category_mapping[category]))
                            try:
                                with closing(urlopen(image_url)) as image:
                                    product.pictures.add(Picture.objects.create(
                                        image=uploadedfile.SimpleUploadedFile(
                                            name='img', content=image.read())
                                    ))
                            except HTTPError as e:
                                print '\nerror loading image for object at url:', self.base_url + product_url

                            # Add the price to the product
                            try:
                                product.prices.add(Price(amount=price, unit=UNIT.DAY))
                                sys.stdout.flush()
                            except:
                                print 'PRICE ERROR'
                                pass
                        except:
                            print 'CANNOT CREATE PRODUCT %s' % summary
                            pass

            except HTTPError:
                print 'error loading page for object at url', self.base_url


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
            self.patron = Patron.objects.get(username='PierreAndreLocation')
        except Patron.DoesNotExist:
            print "Can't find user 'PierreAndreLocation'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
        '/transport-manutention/',
        '/travail-en-hauteur/',
        '/chauffage/',
        '/gros-oeuvre/',
        '/second-oeuvre/outillage-pneumatique/',
        '/second-oeuvre/perforateur-burineur-piqueur-brise-béton/',
        '/second-oeuvre/scie-découpeuse-carotteuse-meuleuse/',
        '/second-oeuvre/ponçage-du-sol/',
        '/second-oeuvre/rénovation-sol-et-mur/',
        '/second-oeuvre/perceuse-boulonneuse/',
        '/second-oeuvre/ponçage/',
        '/second-oeuvre/travail-du-bois/',
        '/second-oeuvre/peinture-laque-crépi/',
        '/second-oeuvre/soudure/',
        '/second-oeuvre/divers/',
        '/nettoyage/',
        '/espaces-verts/',
        ]
        
        # List the products and create the product in the database
        for i in xrange(thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()