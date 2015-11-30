# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading, string
from contextlib import closing

category_mapping = { 
	'/location-de-chaussures-d-alpinisme,fr,3,46.cfm':'alpiniste',
	'/location-de-chaussures-d-expedition,fr,3,79.cfm':'alpiniste',
	'/location-de-chaussons-d-escalade,fr,3,141.cfm' : 'escalade',

	'/location-de-pantalons-de-ski,fr,3,249.cfm':'pantalon-et-jean',
	'/location-de-veste-conditions-extremes,fr,3,232.cfm':'manteau-et-blouson',
	'/location-de-pant-combi-conditions-extremes,fr,3,233.cfm' : 'pantalon-et-jean',
	'/location-de-moufles-extremes,fr,3,234.cfm':'veste-et-costume',
	'/location-accessoires-conditions-extremes,fr,3,235.cfm':'boots',
	'/location-de-vetements-en-gore-tex,fr,3,81.cfm' : 'veste-et-costume',
	'/location-de-vetements-specifique-mont-blanc,fr,3,230.cfm':'manteau-et-blouson',
	'/location-de-vetements-en-gore-tex,fr,3,207.cfm':'manteau',

	'/location-de-baudriers-avec-mousqueton,fr,3,74.cfm' : 'escalade',
	'/location-de-crampons-avec-anti-botte,fr,3,73.cfm':'alpiniste',
	'/location-de-piolet,fr,3,75.cfm':'alpiniste',
	'/location-de-casques,fr,3,76.cfm' : 'alpiniste',
	'/location-de-baton-telescopique,fr,3,70.cfm':'alpiniste',
	'/location-de-lampe-frontale,fr,3,77.cfm':'alpiniste',
	'/location-de-longe-de-via-ferrata,fr,3,78.cfm' : 'alpiniste',
	'/location-de-masques-d-altitude,fr,3,98.cfm':'alpiniste',
	'/location-de-pack-d-alpinisme,fr,3,58.cfm':'alpiniste',
	'/location-de-sac-a-dos,fr,3,63.cfm' : 'alpiniste',
	'/location-de-sacs-etanches,fr,3,92.cfm':'alpiniste',
	'/location-de-sacs-gros-volume,fr,3,91.cfm':'alpiniste',
	'/location-de-rechauds,fr,3,88.cfm' : 'alpiniste',
	'/location-d-appareil-de-traitement-de-l-eau,fr,3,87.cfm':'alpiniste',
	'/location-d-eclairages,fr,3,86.cfm':'alpiniste',
	'/location-de-popotes,fr,3,212.cfm' : 'alpiniste',
	'/location-de-cuisiniere,fr,3,213.cfm':'alpiniste',


	'/location-de-matelas,fr,3,60.cfm':'accessoires-de-camping',
	'/location-de-sac-de-couchage,fr,3,82.cfm':'accessoires-de-camping',

	'/location-de-tente,fr,3,84.cfm' : 'tente',
	'/location-de-tente-douche-de-toilette,fr,3,89.cfm':'tente',
	'/location-de-tente-d-alpinisme,fr,3,2.cfm':'tente',

	'/location-de-vetements-en-duvet,fr,3,80.cfm' : 'alpiniste',
	'/location-de-pack-d-expedition,fr,3,96.cfm':'alpiniste',
	'/location-de-pulka,fr,3,94.cfm':'alpiniste',
	'/location-sac-a-dos-d-expedition,fr,3,90.cfm' : 'alpiniste',
	'/location-de-skis-pour-expedition,fr,3,97.cfm':'ski',

	'/location-de-panneaux-solaires,fr,3,102.cfm':'alpiniste',
	'/location-de-gps-terrestre,fr,3,104.cfm' : 'randonneemarin',
	'/location-de-telephone-satellite,fr,3,99.cfm':'telephone-portable',

	'/location-de-skis,fr,3,64.cfm':'ski',
	'/location-de-chaussures-de-ski,fr,3,66.cfm' : 'ski',
	'/location-pack-skis,fr,3,71.cfm':'ski',
	'/location-de-masques-de-ski,fr,3,197.cfm' : 'ski',
	'/location-d-arva,fr,3,67.cfm':'randonnee',
	'/location-de-pelles-et-sondes,fr,3,68.cfm' : 'randonnee',
	'/location-de-peaux-et-couteaux,fr,3,69.cfm':'randonnee',
	'/location-de-raquettes-a-neige,fr,3,72.cfm': 'randonnee',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'hwoog'"
    
    base_url = 'http://www.montagne-expedition.fr'
    thread_num = 1

    def _subpage_crawler(self):
        """Create the list of products by finding the link of each product page"""
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                #print "ERREUR DE LINDEX"
                break
            #print self.base_url + family
            
            with closing(urlopen(self.base_url + family)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
                product_list = product_list_soup.find_all('div',class_='modele_Liste_C')

                for product in product_list:
                	product_url = product.find('a').get('href')
                	self.product_links[self.base_url + family + product_url] = family

                #print self.product_links

    def _product_crawler(self):
        from products.models import Product, Picture, Price

        # Return the price in the right format
        def _to_decimal(s):
            from decimal import Decimal as D
            s2 = s.strip().replace(u'Location à partir de', '').replace(',', '.').replace(' ', '')
            #print s2
            return s2 

        while True:
            try:  
                product_url, category = self.product_links.popitem()
            except KeyError:
            	#print KeyError
                break

            try:
                with closing(urlopen(product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
                    #print product_soup
            except HTTPError:
                print 'error loading page for object at url', product_url


            #Get the image
            try:
                image_href = product_soup.find('a', class_="elevatezoom-gallery").find('img').get('src')
                #print image_href
                image_url = " %s/boutique/%s" % (self.base_url, image_href)
                #print image_url
            except:
                print "pass image"
                pass

            #Get the title
            try:
                summary = product_soup.find('h1').text
                #print summary
            except:
                print "pass title"
                pass
            
            # Get the description
            try:
                description = product_soup.find('span', id='texte_description_fiche_produit').text
                #print description
            except:
                print 'pass description'
                pass

            # Get the price
            try:
                price1 = product_soup.find('span', id='texte_prix_si_prix_desactive').text
                price2 = re.findall('\d+', price1)
                price = "%s.%s" % (int(price2[0]), int(price2[1]))
                #print price
            except:
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
                #print product.address
                try:
                    #print "try upload image"
                    with closing(urlopen(image_url)) as image:
                        product.pictures.add(Picture.objects.create(
                            image=uploadedfile.SimpleUploadedFile(
                                name='img', content=image.read())
                        )
                    )
                    #print image
                except HTTPError as e:
                    print '\nerror loading image for object at url:', family

                # Add the price to the product
                try:
                	product.prices.add(Price(amount=price, unit=UNIT.DAY))
                except:
                    print 'PRICE ERROR'
                    pass
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
            self.patron = Patron.objects.get(username='montagneexpedition')
        except Patron.DoesNotExist:
            print "Can't find user 'Event-location montagneexpedition'"
            return

        # Get the default address of the user to add to the product
        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        # Get families list of products
        self.product_families = [
		'/location-de-chaussures-d-alpinisme,fr,3,46.cfm',
		'/location-de-chaussures-d-expedition,fr,3,79.cfm',
		'/location-de-chaussons-d-escalade,fr,3,141.cfm',

		'/location-de-pantalons-de-ski,fr,3,249.cfm',
		'/location-de-veste-conditions-extremes,fr,3,232.cfm',
		'/location-de-pant-combi-conditions-extremes,fr,3,233.cfm',
		'/location-de-moufles-extremes,fr,3,234.cfm',
		'/location-accessoires-conditions-extremes,fr,3,235.cfm',
		'/location-de-vetements-en-gore-tex,fr,3,81.cfm',
		'/location-de-vetements-specifique-mont-blanc,fr,3,230.cfm',
		'/location-de-vetements-en-gore-tex,fr,3,207.cfm',

		'/location-de-baudriers-avec-mousqueton,fr,3,74.cfm',
		'/location-de-crampons-avec-anti-botte,fr,3,73.cfm',
		'/location-de-piolet,fr,3,75.cfm',
		'/location-de-casques,fr,3,76.cfm',
		'/location-de-baton-telescopique,fr,3,70.cfm',
		'/location-de-lampe-frontale,fr,3,77.cfm',
		'/location-de-longe-de-via-ferrata,fr,3,78.cfm',
		'/location-de-masques-d-altitude,fr,3,98.cfm',
		'/location-de-pack-d-alpinisme,fr,3,58.cfm',
		'/location-de-sac-a-dos,fr,3,63.cfm',
		'/location-de-sacs-etanches,fr,3,92.cfm',
		'/location-de-sacs-gros-volume,fr,3,91.cfm',
		'/location-de-rechauds,fr,3,88.cfm',
		'/location-d-appareil-de-traitement-de-l-eau,fr,3,87.cfm',
		'/location-d-eclairages,fr,3,86.cfm',
		'/location-de-popotes,fr,3,212.cfm',
		'/location-de-cuisiniere,fr,3,213.cfm',


		'/location-de-matelas,fr,3,60.cfm',
		'/location-de-sac-de-couchage,fr,3,82.cfm',

		'/location-de-tente,fr,3,84.cfm',
		'/location-de-tente-douche-de-toilette,fr,3,89.cfm',
		'/location-de-tente-d-alpinisme,fr,3,2.cfm',

		'/location-de-vetements-en-duvet,fr,3,80.cfm',
		'/location-de-pack-d-expedition,fr,3,96.cfm',
		'/location-de-pulka,fr,3,94.cfm',
		'/location-sac-a-dos-d-expedition,fr,3,90.cfm',
		'/location-de-skis-pour-expedition,fr,3,97.cfm',

		'/location-de-panneaux-solaires,fr,3,102.cfm',
		'/location-de-gps-terrestre,fr,3,104.cfm',
		'/location-de-telephone-satellite,fr,3,99.cfm',

		'/location-de-skis,fr,3,64.cfm',
		'/location-de-chaussures-de-ski,fr,3,66.cfm',
		'/location-pack-skis,fr,3,71.cfm',
		'/location-de-masques-de-ski,fr,3,197.cfm',
		'/location-d-arva,fr,3,67.cfm',
		'/location-de-pelles-et-sondes,fr,3,68.cfm',
		'/location-de-peaux-et-couteaux,fr,3,69.cfm',
		'/location-de-raquettes-a-neige,fr,3,72.cfm',
        ]

        #self._subpage_crawler()
        #self._product_crawler()

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

