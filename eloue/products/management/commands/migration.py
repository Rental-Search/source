# -*- coding: utf-8 -*-
import MySQLdb

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode, smart_str

from geocoders.google import geocoder

from eloue.accounts.models import Patron, Address, PhoneNumber
from eloue.products.models import Category

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

def cleanup_phone_number(phone_number):
    """Cleanup phone number format"""
    return phone_number.replace('O', '0').replace('.', '').replace('o', '').replace(' ', '').replace('/', '')

class Command(BaseCommand):
    def import_category_tree(self, cursor):
        mapping = {}
        cursor.execute("""SELECT category_id, category_name FROM abs_vm_category""")
        result_set = cursor.fetchall()
        for row in result_set:
            name = smart_unicode(row['category_name'], encoding='latin1') # encode in utf-8
            category = Category.objects.create(name=name, slug=slugify(name))
            mapping[category.id] = int(row["category_id"])
        mapping_inv = dict((v,k) for k, v in mapping.iteritems())
        for category in Category.objects.iterator():
            cursor.execute("""SELECT category_parent_id FROM abs_vm_category_xref WHERE category_child_id = %d""" % mapping[category.id])
            row = cursor.fetchone()
            original_parent_id = int(row["category_parent_id"])
            if original_parent_id != 0: # don't add parent to root category 
                parent_id = mapping_inv[original_parent_id]
                category.parent_id = parent_id
                category.save()
    
    def import_members(self, cursor):
        # TODO : Add lat, long
        geocode = geocoder('ABQIAAAA7bPNcG5t1-bTyW9iNmI-jRRqVDjnV4vohYMgEqqi0RF2UFYT-xSSwfcv2yfC-sACkmL4FuG-A_bScQ')
        cursor.execute("""SELECT id, username, email, password, registerDate, activation, lat, 'long' FROM abs_users""")
        result_set = cursor.fetchall()
        for row in result_set:
            username = smart_unicode(row['username'], encoding='latin1')
            email = smart_unicode(row['email'], encoding='latin1')
            password = "md5$$%s" % row['password']
            date_joined = row['registerDate']
            activation_key = smart_unicode(row['activation'], encoding='latin1')
            lat, lon = row['lat'], row['long']
            
            if not activation_key:
                patron = Patron.objects.create_user(username, email, password)
                patron.date_joined = date_joined
                patron.save()
            else:
                patron = Patron.objects.create_inactive(username, email, password, send_email=False) # TODO : THIS IS SENDING AN EMAIL DUDE
                patron.date_joined = date_joined
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
                
                city = smart_unicode(user_info['city'], encoding='latin1')
                zipcode = smart_unicode(user_info['zip'], encoding='latin1')
                country = COUNTRIES_MAP[user_info['country']]
                
                if address1 and country:
                    name, (lat, lon) = geocode(smart_str("%s %s %s %s" % (address1, address2, zipcode, city)))
                    patron.addresses.create(
                        civility=CIVILITY_MAP[user_info['title']],
                        address1=address1,
                        address2=address2,
                        zipcode=zipcode,
                        city=city,
                        country=country,
                        lat=lat,
                        lon=lon
                    )
                
                if user_info['phone_1']:
                    patron.phones.create(number=smart_unicode(cleanup_phone_number(user_info['phone_1']), encoding='latin1'), kind=4)
                
                if user_info['phone_2']:
                    patron.phones.create(number=smart_unicode(cleanup_phone_number(user_info['phone_2']), encoding='latin1'), kind=4)
                    
                if user_info['fax']:
                    patron.phones.create(number=smart_unicode(cleanup_phone_number(user_info['fax']), encoding='latin1'), kind=3)
                
                patron.save()
    
    def handle(self, *args, **options):
        connection = MySQLdb.connect(unix_socket='/tmp/mysql.sock', user='root', passwd='facteur', db="eloueweb")
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        self.import_category_tree(cursor)
        self.import_members(cursor)
    
