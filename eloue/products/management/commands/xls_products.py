#!/usr/bin/python
# -*- coding: utf-8 -*-
import logbook
import xlrd
from lxml import etree
import urllib2
import httplib
import pprint
import gzip
import io
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files import uploadedfile

BASE_URL = 'http://www.spotsound.fr'

def next_row(sheet, row):
    return (unicode(sheet.cell(row, i).value) for i in xrange(sheet.ncols))

category_mapping = {
    u'Sonorisation': 359,
    u'Enceintes': 360, 
    u'Packs Soirée': 373,
    u'Packs Universels Musique a  30 euros': 373,
    u'Eclairage': 373,
    u'Lasers': 375,
    u'Eclairages a  Halogenes': 374,
    u'Tubes néon': 373,
    u'Eclairages pour theatre': 373,
    u'Machines spéciales': 354,
    u'Accessoires': 357,
    u'Déguisements': 561,
    u'Divers': 354,
    u'Machines Festives - Organisation fêtes': 354,
    u'Structures': 2698,
    u'Cablerie': 357,
    u'Machines a  fumée': 354
}

log = logbook.Logger('eloue.products.management.commands.xls_products')

class Command(BaseCommand):
    args = '<xml_file.xml>'
    help = "Imports given xls file for user 'spotsound'"

    def handle(self, *args, **options):
        from eloue.products.models import Picture, Price, Product, Category
        from eloue.accounts.models import Patron
        try:
            patron = Patron.objects.get(username='spotsound')
            address = patron.addresses.all()[0]
        except Patron.DoesNotExist:
            print "Can't find user 'spotsound'"
            return
        if len(args) != 1:
            print 'I need exactly one argument, '
            return
        with open(args[0]) as xlsx:
            sheet = xlrd.open_workbook(file_contents=xlsx.read()).sheets()[0]
            rows = iter(xrange(sheet.nrows))
            header = tuple(next_row(sheet, next(rows))) # the header line
            next_row(sheet, next(rows)) # the emtpy line
            find = etree.XPath("//*[@id='image-block']/a/img")
            for row in iter(rows):
                while True:
                    try:
                        product_row = dict(zip(header, next_row(sheet, row)))
                        print row, product_row['nom de la photo']
                        url = product_row['nom de la photo']
                        request = urllib2.Request(url)
                        request.add_header('Accept-Encoding', 'gzip,deflate')
                        response = urllib2.urlopen(request)
                        if response.info().get('Content-Encoding') == 'gzip':
                            response = io.BytesIO(response.read())
                            response = gzip.GzipFile(fileobj=response)
                        html = etree.parse(response, parser=etree.HTMLParser(encoding='utf-8', recover=True, remove_comments=True))
                        img = find(html)
                        request = urllib2.Request(BASE_URL+img[0].attrib['src'])
                        response = urllib2.urlopen(request)
                        if response.info().get('Content-Encoding') == 'gzip':
                            response = io.BytesIO(response.read())
                            response = gzip.GzipFile(fileobj=response)
                        picture = Picture.objects.create(
                            image=uploadedfile.SimpleUploadedFile(
                                name='img', 
                                content=response.read()
                            )
                        )
                        product = Product(
                            summary=product_row['titre'],
                            deposit_amount=product_row['caution'],
                            description = product_row['description'],
                            address = address,
                            quantity = product_row[u'quantité'].replace('.0', ''),
                            owner=patron,
                            category=Category.objects.get(pk=category_mapping[product_row[u'catégorie']])
                        )
                        product.save()
                        day_price = Price(unit=1, amount=product_row[u'Pirx journée'])
                        we_price = Price(unit=2, amount=product_row[u'Prix week end'])
                        week_price = Price(unit=3, amount=product_row[u'Prix semaine'])
                        product.pictures.add(picture)
                        product.prices.add(day_price, we_price, week_price)
                    except (urllib2.HTTPError, urllib2.URLError, httplib.BadStatusLine) as e:
                        log.exception("Exception {0} occured, retry ...".format(e))
                        continue
                    else:
                        break