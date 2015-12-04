# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '925-amplificateurs':'amplificateur',
    '931-platines-cd':'consoles-usb',
    '942-ligne-100v':'connectique',
    '940-ears-monitor':'connectique',
    '964-traitement-du-son':'effets-son',
    '961-pupitres-conferenciers':'structures',
    '966-sonorisation-embarquee-vehicule':'enceintes-dj',
    '950-micros-filaires':'micro-filaire',
    '951-micros-hf':'micro-sans-fil',
    '952-micros-instruments':'micro-filaire',
    '958-consoles-mixages-orchestres':'consoles-usb',
    '932-tables-mixages-dj':'consoles-usb',
    '935-enceintes-passives':'enceintes-dj',
    '936-enceintes-actives':'enceintes-dj',
    '937-systemes-passifs':'enceintes-dj',
    '938-systemes-actifs':'enceintes-dj',
    '939-retours-de-scene':'enceintes-dj',
    '963-sonorisation-portable':'enceintes-dj',
    '1035-cablage-audio':'connectique',
    '926-blocs-de-puissances':'amplificateur',
    '929-consoles-lumieres':'jeu-de-lumiere',
    '927-boules-a-facettes':'boule-a-facette',
    '934-poursuites-et-decoupes':'jeu-de-lumiere',
    '944-lyres-et-scans':'lyres',
    '943-lasers':'laser',
    '968-effets-lumineux':'jeu-de-lumiere',
    '1043-lumiere-noire':'lumiere-noire',
    '959-stroboscopes':'stroboscope',
    '965-eclairages-architecturales-spectacles-et-decorations':'jeu-de-lumiere',
    '1037-cables-dmx-et-autres':'connectique',
    '946-machines-a-fumee-brouillard':'machine-fumee',
    '947-machines-a-bulles-':'machine-bulle',
    '948-machines-a-mousse-neige':'machine-fumee',
    '949-machines-a-confettis':'machine-bulle',
    '1046-projecteurs-de-ciel-et-traceurs':'jeu-de-lumiere',
    '1049-machine-a-fumee-lourde-':'machine-fumee',
    '930-decorations-led':'jeu-de-lumiere',
    '996-mobiliers-lumineux':'jeu-de-lumiere',
    '997-bars':'jeu-de-lumiere',
    '998-colonnes':'jeu-de-lumiere',
    '1000-pots':'jeu-de-lumiere',
    '1001-boules':'jeu-de-lumiere',
    '1002-cubes':'jeu-de-lumiere',
    '1003-location-seau-a-champagne':'structures',
    '1047-ballon-eclairant':'jeu-de-lumiere',
    '962-videos-projecteurs':'videoprojecteur',
    '1042-ecrans-led':'jeu-de-lumiere',
    '941-lecteurs-videos':'videoprojecteur',
    '1024-ecrans-de-projection':'videoprojecteur',
    '1036-cables-':'connectique',
    '945-karaoke':'jeux-de-bistrot',
    '953-packs-dj':'controleur-dmx',
    '954-packs-lights':'jeu-de-lumiere',
    '955-packs-son-et-lights':'jeu-de-lumiere',
    '969-packs-son':'jeu-de-lumiere',
    '1044-location-service-reception':'amplificateur',
    '1034-escaliers-':'structures',
    '960-structures-et-pieds':'structures',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'hugow'"
    
    base_url = 'http://location.music-and-lights.com/'
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
                product_list = product_list_soup.find_all('h3')
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
                image_url = product_soup.find('a', class_="MagicZoomPlus").find('img').get('src')
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
                description = product_soup.find('div', id='short_description_content').find('p').text
                #print "description : %s" % description
            except:
                description = " "
                print 'pass description'
                pass

            # Get the price
            try:
                price1 = product_soup.find('span', id='our_price_display').text
                price2 = (re.findall('\d+', price1 ))
                price = "%s.%s" % (int(price2[0]), int(price2[1]))
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
            self.patron = Patron.objects.get(username='hugow') #rslocation18 aussi ?
        except Patron.DoesNotExist:
            print "Can't find user 'Music and Lights'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Get families list of products
        self.product_families = [
        '925-amplificateurs',
        '931-platines-cd',
        '942-ligne-100v',
        '940-ears-monitor',
        '964-traitement-du-son',
        '961-pupitres-conferenciers',
        '966-sonorisation-embarquee-vehicule',
        '950-micros-filaires',
        '951-micros-hf',
        '952-micros-instruments',
        '958-consoles-mixages-orchestres',
        '932-tables-mixages-dj',
        '935-enceintes-passives',
        '936-enceintes-actives',
        '937-systemes-passifs',
        '938-systemes-actifs',
        '939-retours-de-scene',
        '963-sonorisation-portable',
        '1035-cablage-audio',
        '926-blocs-de-puissances',
        '929-consoles-lumieres',
        '927-boules-a-facettes',
        '934-poursuites-et-decoupes',
        '944-lyres-et-scans',
        '943-lasers',
        '968-effets-lumineux',
        '1043-lumiere-noire',
        '959-stroboscopes',
        '965-eclairages-architecturales-spectacles-et-decorations',
        '1037-cables-dmx-et-autres',
        '946-machines-a-fumee-brouillard',
        '947-machines-a-bulles-',
        '948-machines-a-mousse-neige',
        '949-machines-a-confettis',
        '1046-projecteurs-de-ciel-et-traceurs',
        '1049-machine-a-fumee-lourde-',
        '1050-consommable-',
        '930-decorations-led',
        '996-mobiliers-lumineux',
        '997-bars',
        '998-colonnes',
        '1000-pots',
        '1001-boules',
        '1002-cubes',
        '1003-location-seau-a-champagne',
        '1047-ballon-eclairant',
        '962-videos-projecteurs',
        '1042-ecrans-led',
        '941-lecteurs-videos',
        '1024-ecrans-de-projection',
        '1036-cables-',
        '945-karaoke',
        '953-packs-dj',
        '954-packs-lights',
        '955-packs-son-et-lights',
        '969-packs-son',
        '1044-location-service-reception',
        '1034-escaliers-',
        '960-structures-et-pieds',
        '925-amplificateurs',
        '925-amplificateurs',
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

