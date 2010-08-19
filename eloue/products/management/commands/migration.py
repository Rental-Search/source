# -*- coding: utf-8 -*-
import MySQLdb

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode

from eloue.products.models import Patron
from eloue.products.models import Category

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
        # TODO : Add lat, long and address
        cursor.execute("""SELECT username, email, password, registerDate, activation, lat, 'long' FROM abs_users""")
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
    
    def handle(self, *args, **options):
        connection = MySQLdb.connect(unix_socket='/tmp/mysql.sock', user='root', passwd='facteur', db="eloueweb")
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        #self.import_category_tree(cursor)
        self.import_members(cursor)
    
