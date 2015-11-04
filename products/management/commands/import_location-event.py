# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '/28-lumiere-noire':'lumière noire',
    '/33-stroboscopes/':'strobocope',
    '/34-lasers/':'laser',
    '/35-machines-a-effet/':'strobocope',
    '/44-machine-a-fumee/':'machine à fumée',
    '/45-machine-a-bulles/':'machine à bulle',
    '/76-machine-a-brouillard-/':'machine à fumée',
    '/77-machine-a-mousse/':'machine à fumée',
    '/36-projecteur-traditionnel/':'spot',
    '/37-accessoires-eclairages/':'eclairage',
    '/38-bloc-de-puissance/':'eclairage',
    '/39-consoles-lumiere/':'eclairage',
    '/41-packs-lumiere-sans-sono/':'jeu de lumière',
    '/42-effet-lumieres/':'jeu de lumière',
    '/43-scanner-et-lyres-dmx/':'lyres',
    '/70-location-consoles-video-ps4xbox-one-wii/':'jeux vidéo',
    '/81-videoprojecteur/':'vidéoprojecteur',
    '/18-nos-packs-son-eclairage/':'jeu de lumière',
    '/20-location-flight-case/':'équipement DJ',
    '/40-location-structure/':'extérieurs',
    '/53-location-de-nacelle/':'travaux',
    '/30-table-de-mixage/':'télévision',
    '/31-micro/':'télévision',
    '/32-packs-sono-sans-lumiere/':'télévision',
    '/66-platines-dj-cd-et-midi/':'télévision',
    '/71-boitier-de-scene-multipaires/':'télévision',
    '/83-caissons-de-basses/':'télévision',
    '/84-enceintes-sono/':'enceinte DJ',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'hwoog'"
    
    base_url = 'http://location-events.fr'

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break
            print self.base_url + family
            
            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('div',class_='product-container')
                for product in product_list:
                    product_url = product.find('a').get('href')
                    self.product_links[product_url] = self.base_url + family
                print self.product_links

        

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
            self.patron = Patron.objects.get(username='hwoog')
        except Patron.DoesNotExist:
            print "Can't find user 'Event-location hwoog'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
		'/28-lumiere-noire',
		'/33-stroboscopes/',
		'/34-lasers/',
		'/35-machines-a-effet/',
		'/44-machine-a-fumee/',
		'/45-machine-a-bulles/',
		'/76-machine-a-brouillard-/',
		'/77-machine-a-mousse/',
		'/36-projecteur-traditionnel/',
		'/37-accessoires-eclairages/',
		'/38-bloc-de-puissance/',
		'/39-consoles-lumiere/',
		'/41-packs-lumiere-sans-sono/',
		'/42-effet-lumieres/',
		'/43-scanner-et-lyres-dmx/',
		'/70-location-consoles-video-ps4xbox-one-wii/',
		'/81-videoprojecteur/',
		'/18-nos-packs-son-eclairage/',
		'/20-location-flight-case/',
		'/40-location-structure/',
		'/53-location-de-nacelle/',
		'/30-table-de-mixage/',
		'/31-micro/',
		'/32-packs-sono-sans-lumiere/',
		'/66-platines-dj-cd-et-midi/',
		'/71-boitier-de-scene-multipaires/',
		'/83-caissons-de-basses/',
		'/84-enceintes-sono/',
        ]
        
        # List the products and create the product in the database
        for i in xrange(thread_num):
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


