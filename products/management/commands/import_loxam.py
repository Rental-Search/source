# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '/location/terrassement/location-excavation/pg90-0-0.html':'travaux',
    '/location/terrassement/location-accessoires-terrassement/pg538-0-0.html':'travaux',
    '/location/terrassement/pompage-brumisation/location-pompe-immergee/pg2522-0-0.html':'pompe-immergee',
    '/location/terrassement/pompage-brumisation/location-pompe-de-surface/pg2523-0-0.html':'pompe-devacuation',
    '/location/terrassement/pompage-brumisation/location-brumisation/pg2559-0-0.html':'ventilateur',
    '/location/terrassement/topographie/location-niveaux-optiques-et-niveaux-laser/pg86-0-0.html':'niveau-laser',
    '/location/remblayage/location-chargeuse/pg2524-0-0.html':'travaux',
    '/location/remblayage/location-dumper-et-transporteur-sur-chenilles/pg2525-0-0.html':'travaux',
    '/location/compactage/location-plaque-vibrante-pilonneuse-rouleau/pg2526-0-0.html':'travaux',
    '/location/compactage/location-compacteur-tandem-mixte-monobille/pg2527-0-0.html':'epandeur-rouleau',
    '/location/espaces-verts/location-preparation-des-sols/pg2519-0-0.html':'motobineuse-et-motoculteur',
    '/location/espaces-verts/location-materiel-de-coupe-et-transport-espaces-verts/pg2468-0-0.html':'travaux',
    '/location/transport/location-camion-benne-100-km-inclus/pg96-0-0.html':'utilitaire',
    '/location/transport/location-remorque-citerne-a-eau/pg97-0-0.html':'remorque-utilitaire',
    '/location/elevation/location-nacelle-automotrice-fixe-sur-vl/pg1869-0-0.html':'echafaudage',
    '/location/elevation/location-plate-forme-electrique-et-diesel/pg1867-0-0.html':'echafaudage',
    '/location/elevation/location-echafaudage-plate-forme-individuelle-table-de-macon/pg2529-0-0.html':'echafaudage',
    '/location/manutention/location-chariot-a-mat-vertical/pg1880-0-0.html':'echafaudage',
    '/location/manutention/location-chariot-telescopique/pg2534-0-0.html':'echafaudage',
    '/location/manutention/materiel-de-levage/location-monte-materiaux-treuil-leve-panneau-transpalette/pg2535-0-0.html':'echafaudage',
    '/location/base-vie-et-securite-chantier/location-constructions-modulaires/pg2538-0-0.html':'constructions-modulaires',
    '/location/base-vie-et-securite-chantier/location-installation-de-chantier/pg2539-0-0.html':'constructions-modulaires',
    '/location/alimentation-electrique-eclairage/location-groupes-electrogenes/pg142-0-0.html':'groupe-electrogene',
    '/location/alimentation-electrique-eclairage/location-armoires-electriques-testeurs-electriques/pg1876-0-0.html':'compteur-de-chantier',
    '/location/alimentation-electrique-eclairage/signalisation-eclairage/location-feux-de-chantiers-eclairage/pg145-0-0.html':'constructions-modulaires',
    '/location/alimentation-electrique-eclairage/location-soudage/pg1888-0-0.html':'fer-a-souder-electrique',
    '/location/air-comprime-demolition/location-compresseur/pg2544-0-0.html':'compresseur',
    '/location/air-comprime-demolition/location-outillage-demolition-pneumatique-hydraulique/pg2545-0-0.html':'marteau-piqueur',
    '/location/air-comprime-demolition/location-outillage-electrique/pg2494-0-0.html':'marteau-piqueur',
    '/location/air-comprime-demolition/location-materiel-d-evacuation/pg2502-0-0.html':'travaux',
    '/location/traitement-du-beton/location-preparation-malaxage/pg2546-0-0.html':'betonniere',
    '/location/traitement-du-beton/location-vibration-surfacage/pg2547-0-0.html':'travaux',
    '/location/traitement-du-beton/location-rectification-poncage-beton-marbre/pg2548-0-0.html':'ponceuse',
    '/location/sciage-et-perforation/location-sciage/pg171-0-0.html':'scie-circulaire',
    '/location/sciage-et-perforation/location-perforation/pg1862-0-0.html':'perforateur',
    '/location/fixation/location-cloueur-visseuse/pg2549-0-0.html':'travaux',
    '/location/fixation/location-perceuse-visseuse-electroportative/pg2560-0-0.html':'perceuse-sans-fil',
    '/location/plomberie-genie-climatique/location-plomberie/pg1864-0-0.html':'soudure-et-plomberie',
    '/location/plomberie-genie-climatique/location-diagnostic-controle-maintenance/pg2550-0-0.html':'soudure-et-plomberie',
    '/location/plomberie-genie-climatique/location-chauffage-climatisation-ventilation/pg2511-0-0.html':'chauffage',
    '/location/traitement-sols-et-murs/location-poncage-decapage/pg2552-0-0.html':'ponceuse',
    '/location/traitement-sols-et-murs/location-enduisage-malaxage-peinture/pg2553-0-0.html':'travaux',
    '/location/traitement-sols-et-murs/location-isolation/pg2558-0-0.html':'deshumificateur',
    '/location/sablage-nettoyage/location-sablage-nettoyage/pg2554-0-0.html':'decapeuse',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'DEGUIZLAND'"
    
    base_url = 'http://www.loxam.fr'
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
                product_list = product_list_soup.find_all('div',class_='prodti')
                for product in product_list:
                    product_url = product.find('a').get('href')
                    self.product_links[product_url] = family
                # print self.product_links
  
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
            # product_url = quote(product_url)
            try:
                with closing(urlopen(self.base_url + product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', self.base_url + product_url


            # Get the image
            image_url = product_soup.find('form', id='caddy').find('img').get('src')
            image_url = quote(image_url)

            # Get the title
            infosProduits = product_soup.find('form', id='caddy').find('h1').text
            print infosProduits

            # Get the price
            # price = product_soup.find('div', class_='prix-val').text
            prices = product_soup.find('table', class_='bloc-tarif-part').find_all('td', class_='detail_prix')
            price = prices[0].text
            price = _to_decimal(price)


            # Get the description
            description = product_soup.find('div', id='descrlongue').text
            if len(prices) == 5:
                description += '\n' + prices[4].text + u'€'

            # Format the title
            summary = infosProduits

            deposit_amount = 0.0

            # Create the product
            from products.models import Category, Price
            from products.choices import UNIT
            product = Product.objects.create(
                summary=summary, description=description, 
                deposit_amount=deposit_amount, address=self.address, owner=self.patron,
                category=Category.objects.get(slug=category_mapping[category]))
            try:
                with closing(urlopen(self.base_url + image_url)) as image:
                    product.pictures.add(Picture.objects.create(
                        image=uploadedfile.SimpleUploadedFile(
                            name='img', content=image.read())
                    )
                )
            except HTTPError as e:
                print '\nerror loading image for object at url:', self.base_url + product_url
            
            # Add the price to the product
            product.prices.add(Price(amount=price, unit=UNIT.DAY))
            sys.stdout.write('.')
            sys.stdout.flush()


    def handle(self, *args, **options):
        from accounts.models import Patron, Address
        self.product_links = {}

        # Get the user
        try:
            self.patron = Patron.objects.get(username='LOXAM')
        except Patron.DoesNotExist:
            print "Can't find user 'deguizeland'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Configure the parser
        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        # Get families list of products
        self.product_families = [
            '/location/terrassement/location-excavation/pg90-0-0.html',
            '/location/terrassement/location-accessoires-terrassement/pg538-0-0.html',
            '/location/terrassement/pompage-brumisation/location-pompe-immergee/pg2522-0-0.html',
            '/location/terrassement/pompage-brumisation/location-pompe-de-surface/pg2523-0-0.html',
            '/location/terrassement/pompage-brumisation/location-brumisation/pg2559-0-0.html',
            '/location/terrassement/topographie/location-niveaux-optiques-et-niveaux-laser/pg86-0-0.html',
            '/location/remblayage/location-chargeuse/pg2524-0-0.html',
            '/location/remblayage/location-dumper-et-transporteur-sur-chenilles/pg2525-0-0.html',
            '/location/compactage/location-plaque-vibrante-pilonneuse-rouleau/pg2526-0-0.html',
            '/location/compactage/location-compacteur-tandem-mixte-monobille/pg2527-0-0.html',
            '/location/espaces-verts/location-preparation-des-sols/pg2519-0-0.html',
            '/location/espaces-verts/location-materiel-de-coupe-et-transport-espaces-verts/pg2468-0-0.html',
            '/location/transport/location-camion-benne-100-km-inclus/pg96-0-0.html',
            '/location/transport/location-remorque-citerne-a-eau/pg97-0-0.html',
            '/location/elevation/location-nacelle-automotrice-fixe-sur-vl/pg1869-0-0.html',
            '/location/elevation/location-plate-forme-electrique-et-diesel/pg1867-0-0.html',
            '/location/elevation/location-echafaudage-plate-forme-individuelle-table-de-macon/pg2529-0-0.html',
            '/location/manutention/location-chariot-a-mat-vertical/pg1880-0-0.html',
            '/location/manutention/location-chariot-telescopique/pg2534-0-0.html',
            '/location/manutention/materiel-de-levage/location-monte-materiaux-treuil-leve-panneau-transpalette/pg2535-0-0.html',
            '/location/base-vie-et-securite-chantier/location-constructions-modulaires/pg2538-0-0.html',
            '/location/base-vie-et-securite-chantier/location-installation-de-chantier/pg2539-0-0.html',
            '/location/alimentation-electrique-eclairage/location-groupes-electrogenes/pg142-0-0.html',
            '/location/alimentation-electrique-eclairage/location-armoires-electriques-testeurs-electriques/pg1876-0-0.html',
            '/location/alimentation-electrique-eclairage/signalisation-eclairage/location-feux-de-chantiers-eclairage/pg145-0-0.html',
            '/location/alimentation-electrique-eclairage/location-soudage/pg1888-0-0.html',
            '/location/air-comprime-demolition/location-compresseur/pg2544-0-0.html',
            '/location/air-comprime-demolition/location-outillage-demolition-pneumatique-hydraulique/pg2545-0-0.html',
            '/location/air-comprime-demolition/location-outillage-electrique/pg2494-0-0.html',
            '/location/air-comprime-demolition/location-materiel-d-evacuation/pg2502-0-0.html',
            '/location/traitement-du-beton/location-preparation-malaxage/pg2546-0-0.html',
            '/location/traitement-du-beton/location-vibration-surfacage/pg2547-0-0.html',
            '/location/traitement-du-beton/location-rectification-poncage-beton-marbre/pg2548-0-0.html',
            '/location/sciage-et-perforation/location-sciage/pg171-0-0.html',
            '/location/sciage-et-perforation/location-perforation/pg1862-0-0.html',
            '/location/fixation/location-cloueur-visseuse/pg2549-0-0.html',
            '/location/fixation/location-perceuse-visseuse-electroportative/pg2560-0-0.html',
            '/location/plomberie-genie-climatique/location-plomberie/pg1864-0-0.html',
            '/location/plomberie-genie-climatique/location-diagnostic-controle-maintenance/pg2550-0-0.html',
            '/location/plomberie-genie-climatique/location-chauffage-climatisation-ventilation/pg2511-0-0.html',
            '/location/traitement-sols-et-murs/location-poncage-decapage/pg2552-0-0.html',
            '/location/traitement-sols-et-murs/location-enduisage-malaxage-peinture/pg2553-0-0.html',
            '/location/traitement-sols-et-murs/location-isolation/pg2558-0-0.html',
            '/location/sablage-nettoyage/location-sablage-nettoyage/pg2554-0-0.html',
         ]
        
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