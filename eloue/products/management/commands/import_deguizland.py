# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

from bs4 import BeautifulSoup
import re, sys
from urllib2 import urlopen, quote, HTTPError
import threading
from contextlib import closing

category_mapping = { 
    '/produits/famille/mere-noel': 'pere-noel',
    '/produits/famille/pere-noel': 'pere-noel',
    '/produits/famille/divers': 'aventure',
    '/produits/famille/vampires': 'halloween',
    '/produits/famille/sorciers': 'halloween',
    '/produits/famille/mechants': 'halloween',
    '/produits/famille/mort': 'halloween',
    '/produits/famille/demons': 'halloween',
    '/produits/famille/anges': 'halloween',
    '/produits/famille/sexy': 'sexy',
    '/produits/famille/insolite-amp-enterrement-de-vie-garcon-filles': 'sexy',
    '/produits/famille/fruits-et-legumes': 'animal',
    '/produits/famille/animaux': 'animal',
    '/produits/famille/metiers-et-uniformes': 'uniforme',
    '/produits/famille/clowns': 'aventure',
    '/produits/famille/religieux': 'sexy',
    '/produits/famille/cowboys-et-indiens': 'aventure',
    '/produits/famille/pirates-et-gitanes': 'aventure',
    '/produits/famille/far-west': 'aventure',
    '/produits/famille/folklore': 'pays-du-monde',
    '/produits/famille/russie': 'pays-du-monde',
    '/produits/famille/rome-antique': 'pays-du-monde',
    '/produits/famille/orient': 'pays-du-monde',
    '/produits/famille/mexique': 'pays-du-monde',
    '/produits/famille/grece-antique': 'pays-du-monde',
    '/produits/famille/gaule-antique': 'pays-du-monde',
    '/produits/famille/espagne': 'pays-du-monde',
    '/produits/famille/egypte-antique': 'pays-du-monde',
    '/produits/famille/ecosse': 'pays-du-monde',
    '/produits/famille/bresil': 'pays-du-monde',
    '/produits/famille/asie': 'pays-du-monde',
    '/produits/famille/chevaliers': 'aventure',
    '/produits/famille/mousquetaires': 'historique',
    '/produits/famille/renaissance': 'historique',
    '/produits/famille/annee-80': 'annees-60-70',
    '/produits/famille/disco': 'annees-60-70',
    '/produits/famille/hippies': 'annees-60-70',
    '/produits/famille/annees-50-60': 'annees-60-70',
    '/produits/famille/charleston': 'annees-60-70',
    '/produits/famille/debut-du-20eme-siecle': 'historique',
    '/produits/famille/french-cancan': 'danse',
    '/produits/famille/revolution': 'historique',
    '/produits/famille/moyen-age': 'historique',
    '/produits/famille/prehistoire': 'historique',
    '/produits/famille/justiciers': 'aventure',
    '/produits/famille/princesses': 'princesse',
    '/produits/famille/jeux-video': 'aventure',
    '/produits/famille/star-wars': 'aventure',
    '/produits/famille/manga-et-cosplay': 'aventure',
    '/produits/famille/walt-disney': 'aventure',
    '/produits/famille/stars': 'aventure',
    '/produits/famille/films-et-series': 'aventure',
    '/produits/famille/bd-dessins-animes': 'aventure',
    '/produits/famille/heros-super-heros': 'aventure',
}


class Command(BaseCommand):
    args = ''
    help = "Imports given xls file for user 'DEGUIZLAND'"
    
    base_url = 'http://www.deguizland.com'
    thread_num = 5

    def _subpage_crawler(self):
        while True:
            try:
                family = self.product_families.pop()
            except IndexError:
                break
            family_url = quote(family.get('href'))

            with closing(urlopen(self.base_url + family_url)) as product_list_page:
                product_list_soup = BeautifulSoup(product_list_page, 'html.parser')
            for product in product_list_soup.find_all('div', class_='blocPdtListe'):
                product_url = product.find('a').get('href')
                self.product_links[product_url] = family_url

    def _product_crawler(self):
        from eloue.products.models import Product, Picture, Price
        def _to_decimal(s):
            from decimal import Decimal as D
            return D(s.strip().replace(u'€', '').replace(',', '.').replace(' ', ''))

        while True:
            try:
                product_url, category = self.product_links.popitem()
            except KeyError:
                break
            product_url = quote(product_url)
            try:
                with closing(urlopen(self.base_url + product_url)) as product_page:
                    product_soup = BeautifulSoup(product_page, 'html.parser')
            except HTTPError:
                print 'error loading page for object at url', self.base_url + product_url
            image_url = product_soup.find('div', id='photo').a.get('href')
            image_url = quote(image_url)
            infosProduits = product_soup.find('div', id='infosProduits')
            price = infosProduits.find('div', id='prix').text
            price = _to_decimal(price)
            deposit_amount = infosProduits.find('div', id='composition').find('strong').text
            deposit_amount = _to_decimal(deposit_amount)
            description = infosProduits.find('p', class_='expandable').text
            composition = infosProduits.find('div', id='composition')
            description += composition.h2.text
            description += '\n'
            description += composition.p.text
            summary = infosProduits.h1.text
            from eloue.products.models import Category, Price, UNIT
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
            product.prices.add(Price(amount=price, unit=UNIT.DAY))
            sys.stdout.write('.')
            sys.stdout.flush()


    def handle(self, *args, **options):
        from eloue.accounts.models import Patron, Address
        self.product_links = {}

        try:
            self.patron = Patron.objects.get(username='DEGUIZLAND')
        except Patron.DoesNotExist:
            print "Can't find user 'deguizeland'"
            return

        self.address = self.patron.default_address or self.patron.addresses.all()[0]

        with closing(urlopen(self.base_url)) as main_page:
            self.soup = BeautifulSoup(main_page, 'html.parser')

        self.product_families = self.soup.findAll('a', href=re.compile('famille'))
        
        for i in xrange(self.thread_num):
            threading.Thread(target=self._subpage_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

        print 'Found %d object' % len(self.product_links)

        for i in xrange(self.thread_num):
            threading.Thread(target=self._product_crawler).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

