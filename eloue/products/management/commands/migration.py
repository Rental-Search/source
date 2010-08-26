# -*- coding: utf-8 -*-
import os, MySQLdb

from lxml import html
from optparse import make_option

from django.db import connection
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils.encoding import smart_unicode

CIVILITY_MAP = {
    'Mr':2,
    'Mlle':1,
    'Mme':0,
    'Autre':None,
    '':None,
    None:None
}

COUNTRIES_MAP = {
    'AND':'AD',
    'BEL':'BE',
    'BFA':None,
    'BGD':'FR',
    'CHE':'CH',
    'CAN':'CA',
    'ESP':'ES',
    'FRA':'FR',
    'FXX':'FR',
    'NLD':'NL',
    'REU':'RE',
    'GLP':'GP',
    'MTQ':'MQ',
    'MAR':'MA',
    'TUN':'TN',
    'MCO':'MC',
    'MUS':'MU'
}

PUBLISH_MAP = { # WARN : We invert value because we mark them as archived rather than published
    'Y':False,
    'N':True
}

def cleanup_html_entities(text, method='html'):
    """Remove html entitites from text"""
    if text:
        doc = html.fromstring(text)
        return html.tostring(doc, encoding='utf-8', method=method)
    else:
        return text

def cleanup_phone_number(phone_number):
    """Cleanup phone number format"""
    return phone_number.replace('O', '0').replace('.', '').replace('o', '').replace(' ', '').replace('/', '')

class Command(BaseCommand):
    help = "Migrate data from elouweb to eloue"
    option_list = BaseCommand.option_list + (
        make_option('--migrate-categories',
            action='store_true',
            dest='categories',
            default=False,
            help='Migrate categories tree'
        ),
        make_option('--migrate-members',
            action='store_true',
            dest='members',
            default=False,
            help='Migrate members data'
        ),
        make_option('--migrate-products',
            action='store_true',
            dest='products',
            default=False,
            help='Migrate products data'
        ),
        make_option('--status',
            action='store_true',
            dest='status',
            default=False,
            help='Follow status of migration'
        )
    )

    def import_category_tree(self, cursor, status=False):
        from eloue.products.models import Category
        
        cursor.execute("""SELECT category_id, category_name FROM abs_vm_category""")
        result_set = cursor.fetchall()
        for row in result_set:
            name = smart_unicode(row['category_name'], encoding='latin1') # encode in utf-8
            category = Category.objects.create(id=row['category_id'], name=name, slug=slugify(name))
        for category in Category.objects.iterator():
            cursor.execute("""SELECT category_parent_id FROM abs_vm_category_xref WHERE category_child_id = %d""" % category.id)
            row = cursor.fetchone()
            original_parent_id = int(row["category_parent_id"])
            if original_parent_id != 0: # don't add parent to root category 
                category.parent_id = original_parent_id
                category.save()
    
    def import_members(self, cursor, status=False):
        from eloue.accounts.models import Patron
        
        cursor.execute("""SELECT id, username, email, password, registerDate, activation, lat, 'long' FROM abs_users""")
        result_set = cursor.fetchall()
        for i, row in enumerate(result_set):
            if status:
                print '%s\r' % ' '*20, # clean up row
            
            username = smart_unicode(row['username'], encoding='latin1')
            email = smart_unicode(row['email'], encoding='latin1')
            password = smart_unicode("md5$$%s" % row['password'], encoding='latin1')
            date_joined = row['registerDate']
            activation_key = smart_unicode(row['activation'], encoding='latin1')
            lat, lon = row['lat'], row['long']
            
            if not activation_key:
                patron = Patron.objects.create_user(username, email, password, pk=row['id'])
                patron.date_joined = date_joined
                patron.password = password
                patron.save()
            else:
                patron = Patron.objects.create_inactive(username, email, password, send_email=False, pk=row['id']) # TODO : THIS IS SENDING AN EMAIL DUDE
                patron.date_joined = date_joined
                patron.password = password
                patron.save()
            
            cursor.execute("""SELECT company, title, last_name, first_name, phone_1, phone_2, fax, address_1, address_2, city, country, zip FROM abs_vm_user_info WHERE user_id = %s""" % row['id'])
            user_info = cursor.fetchone()
            if user_info:
                if user_info['company']:
                    patron.company_name = smart_unicode(user_info['company'], encoding='latin1')
                    patron.is_professional = True
                
                address1 = smart_unicode(user_info['address_1'], encoding='latin1') or None
                if address1 and (user_info['address_2'] != '' or user_info['address_2'] != None):
                    address2 = smart_unicode(user_info['address_2'], encoding='latin1')
                else: 
                    address2 = None
                
                patron.civility = CIVILITY_MAP[user_info['title']]
                patron.last_name = smart_unicode(user_info['last_name'], encoding='latin1')
                patron.first_name = smart_unicode(user_info['first_name'], encoding='latin1')
                
                city = smart_unicode(user_info['city'], encoding='latin1')
                zipcode = smart_unicode(user_info['zip'], encoding='latin1')
                country = COUNTRIES_MAP[user_info['country']]
                
                if address1 and country:
                    patron.addresses.create(
                        address1=address1,
                        address2=address2,
                        zipcode=zipcode,
                        city=city,
                        country=country
                    )
                
                if user_info['phone_1']:
                    patron.phones.create(number=smart_unicode(cleanup_phone_number(user_info['phone_1']), encoding='latin1'), kind=4)
                
                if user_info['phone_2']:
                    patron.phones.create(number=smart_unicode(cleanup_phone_number(user_info['phone_2']), encoding='latin1'), kind=4)
                    
                if user_info['fax']:
                    patron.phones.create(number=smart_unicode(cleanup_phone_number(user_info['fax']), encoding='latin1'), kind=3)
                
                patron.save()
            
            if status:
                print ' Migrate members : %d%%' % ((i * 100) / len(result_set)), # note ending with comma
    
    def import_products(self, cursor, status=False):
        from eloue.accounts.models import Patron
        from eloue.products.models import Product, Category
        
        cursor.execute("""SELECT product_id, product_name, product_s_desc, product_desc, count(product_desc) AS quantity, product_full_image, product_publish, prix, caution, vendor_id, product_lat, product_lng, localisation FROM abs_vm_product GROUP BY product_desc, product_name ORDER BY quantity DESC""")
        result_set = cursor.fetchall()
        for i, row in enumerate(result_set):
            if status:
                print '%s\r' % ' '*20, # clean up row
            
            summary = smart_unicode(row['product_name'], encoding='latin1')
            if not row['product_desc'] and row['product_s_desc']:
                description = smart_unicode(row['product_s_desc'], encoding='latin1')
            else:
                description = smart_unicode(row['product_desc'], encoding='latin1')
            
            summary = cleanup_html_entities(summary, method='text')
            description = cleanup_html_entities(description)
            
            vendor_id = int(row['vendor_id'])
            owner = Patron.objects.get(pk=vendor_id)
            if owner.addresses.all():
                position = Point(float(row['product_lat']), float(row['product_lng']))
                address = owner.addresses.distance(position).order_by('distance')[0]
            else:
                print "owner has no addresses : %d" % vendor_id
            
            cursor.execute("""SELECT category_id FROM abs_vm_product_category_xref WHERE product_id = %s""" % row['product_id'])
            result = cursor.fetchone()
            if not result:
                print "no category for product %d" % row['product_id']
            elif result['category_id'] != 0:
                try:
                    category = Category.objects.get(pk=int(result['category_id']))
                except Category.DoesNotExist:
                    print "product :", row['product_id'], "category :", result['category_id']
            else:
                print "no valid category for product %d" % row['product_id']
                continue
            
            product = Product.objects.create(
                pk=row['product_id'],
                summary=summary,
                description=description,
                category=category,
                is_archived=PUBLISH_MAP[row['product_publish']],
                deposit=row['caution'],
                quantity=row['quantity'],
                owner=owner,
                address=address
            )
            
            product.standardprice.create(
                unit=1, amount=row['prix'], currency='EUR'
            )
            
            if row['product_full_image']:
                try: # FIXME : hardcoded path
                    picture = open(os.path.join('/Users/tim/Downloads/elouefile', str(row['vendor_id']), row['product_full_image']))
                    # product.pictures.create(image=picture)`
                except IOError, e:
                    pass # print e
            
            product.save()
            
            if status:
                print ' Migrate products : %d%%' % ((i * 100) / len(result_set)), # note ending with comma
    
    def update_sequence(self):
        db = connection.cursor()
        db.execute("""SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user))""")
        db.execute("""SELECT setval('products_product_id_seq', (SELECT MAX(id) FROM products_product))""")
    
    def handle(self, *args, **options):
        mysql_db = MySQLdb.connect(unix_socket='/tmp/mysql.sock', user='root', passwd='facteur', db="eloueweb")
        cursor = mysql_db.cursor(MySQLdb.cursors.DictCursor)
        status = options.get('status')
        if options.get('categories'):
            self.import_category_tree(cursor, status)
        if options.get('members'):
            self.import_members(cursor, status)
        if options.get('products'):
            self.import_products(cursor, status)
        self.update_sequence()
    
