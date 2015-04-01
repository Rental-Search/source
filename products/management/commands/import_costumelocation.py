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
    '/western,fr,3,7.cfm':'historique',
    '/uniformes-et-metiers,fr,3,14.cfm':'historique',
    '/super-heros-cine-bd-tele,fr,3,11.cfm':'aventure',
    '/super-heros-cine-bd-tele,fr,3,11.cfm?pag=2':'aventure',
    '/super-heros-cine-bd-tele,fr,3,11.cfm?pag=3':'aventure',
    '/second-empire-et-valse-de-vienne,fr,3,6.cfm':'historique',
    '/second-empire-et-valse-de-vienne,fr,3,6.cfm?pag=2':'historique',
    '/second-empire-et-valse-de-vienne,fr,3,6.cfm?pag=3':'historique',
    '/rock-hippie-disco,fr,3,10.cfm':'historique',
    '/robes-du-soir,fr,3,17.cfm':'robe',
    '/robes-de-mariees,fr,3,18.cfm':'robe',
    '/premier-empire,fr,3,5.cfm':'historique',
    '/pirates-et-flibustiers,fr,3,4.cfm':'historique',
    '/moyen-age,fr,3,2.cfm':'historique',
    '/moyen-age,fr,3,2.cfm?pag=2':'historique',
    '/mascottes,fr,3,12.cfm':'animal',
    '/les-pays-folkloriques,fr,3,13.cfm':'pays-du-monde',
    '/les-pays-folkloriques,fr,3,13.cfm?pag=2':'pays-du-monde',
    '/louis-xiii-a-louis-xv,fr,3,3.cfm':'historique',
    '/louis-xiii-a-louis-xv,fr,3,3.cfm?pag=2':'historique',
    '/louis-xiii-a-louis-xv,fr,3,3.cfm?pag=3':'historique',
    '/louis-xiii-a-louis-xv,fr,3,3.cfm?pag=4':'historique',
    '/humouristiques,fr,3,16.cfm':'carnaval',
    '/humouristiques,fr,3,16.cfm?pag=2':'carnaval',
    '/halloween-et-fantastiques,fr,3,15.cfm':'halloween',
    '/location-costumes-de-ceremonies,fr,3,23.cfm':'veste-et-costume',
    '/antiquite-et-prehistoire,fr,3,1.cfm':'historique',
    '/annees-folles-charleston,fr,3,9.cfm':'historique',
    '/annees-folles-charleston,fr,3,9.cfm?pag=2':'historique',
    '/animaux,fr,3,22.cfm':'animal',
    '/animaux,fr,3,22.cfm?pag=2':'animal',
    '/1900,fr,3,8.cfm':'historique',
    '/danse-et-spectacle,fr,3,24.cfm':'danse',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'fiestafolies'"
    
    base_url = 'http://www.costumelocation.com'
    thread_num = 2

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break

            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('table', bgcolor='#EFEEE4')
                for product in product_list:
                    product_url = product.find('a').get('href')
                    product_url = '/' + product_url.split('/')[1]
                    product_url = smart_urlquote(product_url)
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
                with closing(urlopen(self.base_url + product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', self.base_url + product_url

            #no need to parse all the page
            block = product_soup.find('div', id="catalogue_pwb")

            # Get the image
            image_url = block.find('a', id='zoomlightbox').find('img').get('src')
            image_url = self.base_url + '/' + image_url

            # Get the title
            infosProduits = block.find('h1', class_="h1_pwb").find('span', id='grand_titre_nom_produit_fiche_produit').text

            # Get the description
            description = ''
            if block.find('div',id="zoneAttributsSimplesContenu"):
                description = block.find('div', id="zoneAttributsSimplesContenu").text
                description = description.replace(u'\n',' ')

            # Format the title
            summary = infosProduits

            deposit_amount = 0.0

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
                        )
                    )
                except HTTPError as e:
                    print '\nerror loading image for object at url:', self.base_url + product_url

                # Add the price to the product
                try:
                    price = block.find('span', id="zone_prix").find('span', id="prix_pas_promotion_euro_fiche_produit").text
                    price = _to_decimal(price)
                    print price
                    product.prices.add(Price(amount=price, unit=UNIT.DAY))
                    sys.stdout.flush()
                except:
                    'PRICE ERROR'
                    pass    
            except:
                'ERROR : CANNOT create PRODUCT %s' % summary
                pass


    def handle(self, *args, **options):
        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='fiestafolies')
        except Patron.DoesNotExist:
            print "Can't find user 'fiestafolies'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
        '/western,fr,3,7.cfm',
        '/uniformes-et-metiers,fr,3,14.cfm',
        '/super-heros-cine-bd-tele,fr,3,11.cfm',
        '/super-heros-cine-bd-tele,fr,3,11.cfm?pag=2',
        '/super-heros-cine-bd-tele,fr,3,11.cfm?pag=3',
        '/second-empire-et-valse-de-vienne,fr,3,6.cfm',
        '/second-empire-et-valse-de-vienne,fr,3,6.cfm?pag=2',
        '/second-empire-et-valse-de-vienne,fr,3,6.cfm?pag=3',
        '/rock-hippie-disco,fr,3,10.cfm',
        '/robes-du-soir,fr,3,17.cfm',
        '/robes-de-mariees,fr,3,18.cfm',
        '/premier-empire,fr,3,5.cfm',
        '/pirates-et-flibustiers,fr,3,4.cfm',
        '/moyen-age,fr,3,2.cfm',
        '/moyen-age,fr,3,2.cfm?pag=2',
        '/mascottes,fr,3,12.cfm',
        '/les-pays-folkloriques,fr,3,13.cfm',
        '/les-pays-folkloriques,fr,3,13.cfm?pag=2',
        '/louis-xiii-a-louis-xv,fr,3,3.cfm',
        '/louis-xiii-a-louis-xv,fr,3,3.cfm?pag=2',
        '/louis-xiii-a-louis-xv,fr,3,3.cfm?pag=3',
        '/louis-xiii-a-louis-xv,fr,3,3.cfm?pag=4',
        '/humouristiques,fr,3,16.cfm',
        '/humouristiques,fr,3,16.cfm?pag=2',
        '/halloween-et-fantastiques,fr,3,15.cfm',
        '/location-costumes-de-ceremonies,fr,3,23.cfm',
        '/antiquite-et-prehistoire,fr,3,1.cfm',
        '/annees-folles-charleston,fr,3,9.cfm',
        '/annees-folles-charleston,fr,3,9.cfm?pag=2',
        '/animaux,fr,3,22.cfm',
        '/animaux,fr,3,22.cfm?pag=2',
        '/1900,fr,3,8.cfm',
        '/danse-et-spectacle,fr,3,24.cfm',
         ]
        # self.product_families = self.soup.findAll('a', href=re.compile('famille'))
        
        # List the products
        for i in xrange(self.thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

        print 'Found %d object' % len(self.product_links)

        # Create the products in the database
        for i in xrange(self.thread_num):
            threading.Thread(target=self._product_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()