from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db import connection

import mysql.connector

from accounts.models import Patron, PhoneNumber, Address, ProAgency,\
    ImportRecord, ProPackage, Subscription
from products.models import Product, Category, Price, Product2Category, Picture
from collections import namedtuple
from itertools import imap, izip
from accounts.choices import PHONE_TYPES
import signal
from optparse import make_option
from django.template import Template, Context
from products.choices import UNIT
from django.contrib.sites.models import Site
from products.signals import ELOUE_SITE_ID
import sys
from django.utils.datetime_safe import datetime
from django.utils import datetime_safe
import datetime as datetime_orig
import requests
from PIL import Image
from StringIO import StringIO
from django.core.files.storage import DefaultStorage
from django.core.files.base import ContentFile
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from requests.exceptions import HTTPError
import threading


class Command(BaseCommand):
    """
    Import rentalcompare users.
    
    If a user is a vendor, a ProAgency is created and 
    all ads are also imported.
    
    Product attributes are added as text in the description.
    """

    USERS_CHUNK_SIZE = 2000
    
    # How much products to save in one go
    PRODUCTS_CHUNK_SIZE = 5000
 
    ORIGIN = "rentalcompare.com"
    
    FILENAME = "darryl_rentcomp"

    LOGOS_URL = "http://cdn.rentalcompare.com/logo/"
    PICTURES_URL = "http://cdn.rentalcompare.com/uploads/"
    
    PRO_PACKAGE_NAME = "Rentalcompare"

    # Product descriptions will be built with this template
    PRODUCT_DESC_TEMPLATE=\
"""
{{ description }}

{% if width %}
Width: {{ width }}"
{% endif %}
{% if height %}
Height: {{ height }}"
{% endif %}
{% if length %}
Length: {{ length }}"
{% endif %}
{% if weight %}
Weight: {{ weight }} lbs.
{% endif %}
"""
    option_list = BaseCommand.option_list + (
                                             
        # Credentials                                                                                                   
        make_option('--user',
            action='store',
            dest='user',
            default='root'),
        make_option('--password',
            action='store',
            dest='password',
            default='root'),
        make_option('--host',
            action='store',
            dest='host',
            default='127.0.0.1'),
        make_option('--port',
            action='store',
            dest='port',
            default='3306'),
        make_option('--database',
            action='store',
            dest='database',
            default='rentalcompare'),
                                             
        # Other options                                       
        make_option('-d', '--dryrun',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Roll back all changes after command completion'),
        make_option('-e', '--export-skipped',
            action='store_true',
            dest='export-skipped',
            default=False,
            help='Export all skipped objects to a .json file'),
        make_option('--limit-products',
            action='store',
            dest='limit-products',
            default=sys.maxint,
            help='Import only a number of products per user'),
        make_option('--limit-users',
            action='store',
            dest='limit-users',
            default=sys.maxint,
            help='Import only a number of users'),       
        make_option('--logos',
            action='store_true',
            dest='logos',
            default=False,
            help='Imports pro logos'),        
        make_option('--undo',
            action='store_true',
            dest='undo',
            default=False,
            help='Undoes ALL imports done with this command (does not delete images)'), 
        make_option('--index',
            action='store_true',
            dest='index',
            default=False,
            help='Indexes imported users and products'),  
        make_option('--pictures',
            action='store_true',
            dest='pictures',
            default=False,
            help='Imports product pictures'),
        make_option('--threads',
            action='store',
            dest='threads',
            default=4,
            help='Number of threads, for image downloads'),
        make_option('--category',
            action='store',
            dest='category',
            default='687',
            help='Default category id'),
        make_option('--user-type',
            action='store',
            dest='level',
            default=None,
            help='User type: user, administrator, editor, vendor'),   
        )

    def __init__(self):
        BaseCommand.__init__(self)
        self.skipped_users = []
        self.skipped_products = []
        self.skipped_logos = []
        self.skipped_pics = []
        signal.signal(signal.SIGINT, self.handle_interrupt)

    _user_type=None
    def get_user_type(self, cols):
        if self._user_type is None:
            class RcUser(namedtuple("RcUser", cols)):
                @property
                def has_address(self):
                    return self.address1 is not None and \
                        self.city is not None and \
                        self.country is not None
                def make_address(self, user):
                    return Address(patron=user,
                               address1=self.address1,
                               address2=self.address2,
                               city=self.city,
                               zipcode=self.zipcode,
                               state=self.state)
                    
            self._user_type = RcUser
        return self._user_type
            
    _product_type=None
    def get_product_type(self, cols):
        if self._product_type is None:
            self._product_type = namedtuple("RcProduct", cols)
        return self._product_type
    
    
    def get_record_queryset(self):
        return ImportRecord.objects.filter(file_name=self.FILENAME, origin=self.ORIGIN)
    
    def get_imported_products_qs(self):
        return Product.objects.filter(import_record__in=self.get_record_queryset())
        
    def get_imported_users_qs(self):
        return Patron.objects.filter(import_record__in=self.get_record_queryset())
        
    def skip_user(self, tup, reason):
        dic = tup._asdict()
        dic["REASON"] = reason
        del dic["password"]
        del dic["wordpress_password"]
        self.skipped_users.append(dic)


    def skip_product(self, tup, reason):
        dic = tup._asdict()
        dic["REASON"] = reason
        self.skipped_products.append(dic)


    def skip_logo(self, obj, reason):
        dic = {k:v for k,v in obj.__dict__.iteritems()\
                if k in ['username', 'id']}
        dic['avatar'] = obj.avatar.name
        dic['REASON'] = reason
        self.skipped_logos.append(dic)
        
    def skip_picture(self, obj, reason):
        dic = {k:v for k,v in obj.__dict__.iteritems()\
                if k in ['product_id', 'id']}
        dic['image'] = obj.image.name
        dic['REASON'] = reason
        self.skipped_pics.append(dic)
    
    
    def handle_interrupt(self, signal, frame):
        raise CommandError("Aborted by user")
    
    
    def handle(self, *args, **options):
        
        if options['undo']:
            self.handle_undo()
        elif options['logos']:
            self.handle_logos(**options)
        elif options['pictures']:
            self.handle_pictures(args, **options)
        elif options['index']:
            self.handle_index()
        else:
            self.handle_import(*args, **options)
        
        
    def handle_import(self, *args, **options):
        
        credentials_keys = ('user', 'password', 'host', 'port', 'database', )
        
        credentials = {k:v for k,v in options.items() if k in credentials_keys}
        
        dry_run = options['dryrun']
        export_skipped = options['export-skipped']
        lp = int(options['limit-products'])
        lu = int(options['limit-users'])
        cat_id = int(options['category'])
        level = options['level']
        
        user_prg = 0
        prod_prg = 0
        
        user_total = 0
        prod_total = 0
        
        slug_attempt = 0
        
        product_desc_template = Template(self.PRODUCT_DESC_TEMPLATE)
        
        transaction.set_autocommit(False)

        try:
            self.stdout.write("Connecting to {user}:*****@{host}:{port}/{database} ...".format(**credentials))
            cnx = mysql.connector.connect(**credentials)
            c = cnx.cursor()
            del options['password']
        except:
            self.stderr.write("Could not establish connection "
                               +"to the rentalcompare database. Cause:")
            raise
        
        el_c = connection.cursor()
        
        try:
            
            DIVERS_CAT = Category.objects.get(id=cat_id);
            ELOUE_SITE = Site.objects.get(id=ELOUE_SITE_ID)
            propack = ProPackage.objects.create(name=self.PRO_PACKAGE_NAME,
                                                price=0)
            
            ir = ImportRecord.objects.create(origin=self.ORIGIN,
                                             file_name=self.FILENAME,
                                             imported_at=datetime.now())
            
            imported_users_ids = self.get_imported_users_qs().values_list('original_id', flat=True)
            imported_products_ids = self.get_imported_products_qs().values_list('original_id', flat=True)
            
            where = ("where level='%s'" % level) if level else ""
            
            c.execute("select count(*) from ob_users "+where)
            (user_count, ) = c.fetchone()
            user_count = min(user_count, lu)
            
            self.stdout.write("Importing %s users (type=%s)" % (user_count, level if level else "*", ))
            
            c.execute("select * from ob_users "+where+" order by registered desc limit %s", (lu,))
            RcUser = self.get_user_type(c.column_names)
            
            chunk = c.fetchmany(size=self.USERS_CHUNK_SIZE)
            
            username_counts = {}
            
            while len(chunk)>0:
                
                for rc_user in imap(RcUser._make, chunk):
                    
                    user_prg = user_prg + 1
                    
                    if rc_user.id in imported_users_ids:
                        continue
                    
                    email_exists = Patron.objects.exists(email=rc_user.email)
                    
                    mess = "Importing user %5s out of %5s: %-50s" % \
                                      (user_prg, user_count, ("reusing " if email_exists else "") + rc_user.username, )
                    
                    self.stdout.write(mess, ending='\r')
                    
                    if not rc_user.email:
                        # TODO do not skip w/o emails
                        self.skip_user(rc_user, "email missing")
                        continue

                    if not rc_user.email:
                        # TODO do not skip w/o emails
                        self.skip_user(rc_user, "email missing")
                        continue
                    
#                 PRO:
#                     Nom entrprise company
#                     Email email
#                     Nom client 
#                     Username username
#                     is_prof=true
#                     # tel, phonenumber
#                     addr 
#                     site
#                     logo entrepr
#                     desc entrepr
                
                    #general_email ?
                    
                    u = {
                         'username': rc_user.username[:30],
                         'password': rc_user.password,
                         'email': rc_user.email,
                         'first_name': rc_user.display_name[:30],
                         'last_name': rc_user.lastname[:30],
                         'url': rc_user.website if rc_user.website is not None else "",
                         'about': rc_user.about_me,
                         'import_record': ir,
                         'original_id': rc_user.id,
                         'avatar': rc_user.logo,
#                          '': ,
                        }
                        
                    # addresse(s)
                    
                    if rc_user.level == "vendor":
                        
                        if rc_user.phonenumber is None:
                            self.skip_user(rc_user, "pro with no phone")
                            continue
                        
                        if not rc_user.has_address:
                            self.skip_user(rc_user, "pro with no address")
                            continue
                        
                        # pro-specific fields
                        u.update({
                                  'company_name': rc_user.company[:50],
                                  'is_professional': True,
                                  })
                        
                    elif rc_user.level == "user":
                        pass

#                     if email_exists:
#                         # TODO do not skip existing emails
#                         self.skip_user(rc_user, "email exists")
#                         continue
                    
                    if not email_exists:
                        username_counts[rc_user.username] = 0
                        username_base = rc_user.username if len(rc_user.username)<=27 else rc_user.username[:27]
                        new_username = rc_user.username[:30]
                        while Patron.objects.exists(username=new_username):
                            username_counts[rc_user.username] = username_counts[rc_user.username] + 1
                            new_username = username_base + '_' + str(username_counts[rc_user.username])
                        u['username'] = new_username
                    
                        user = Patron(**u)
                        user.init_slug()
                        user.slug = user.slug[:50]
                        slug_base = user.slug if len(user.slug)<=47 else user.slug[:47]
                        slug_attempt = 0
                        while Patron.objects.exists(slug=user.slug):
                            # TODO generate new slug properly
                            slug_attempt = slug_attempt + 1
                            user.slug = slug_base + "-" + str(slug_attempt)
                    else:
                        user = Patron.objects.get(email=rc_user.email)
                        
                    
                    if rc_user.phonenumber is not None:
                        user.default_number = PhoneNumber(patron=user,
                                       number=rc_user.phonenumber,
                                       kind=PHONE_TYPES.OTHER)
                    
                    user.save()
                    
                    # user address
                    if rc_user.has_address:
                        # TODO refactor condition
                        addr = rc_user.make_address(user)
                        addr.save()
                    
                    if rc_user.level == "vendor":

                        # boutique(s)
                        # TODO refactor into User.build_boutique
                        agency = ProAgency.objects.create(patron=user,
                                                 name=rc_user.company,
                                                 phone_number=user.default_number,
                                                 address1=addr.address1,
                                                 address2=addr.address2,
                                                 zipcode=addr.zipcode,
                                                 city=addr.city,
                                                 state=addr.state,
                                                 country=addr.country)
                        
                        Subscription.objects.create(patron=user,
                                                    propackage=propack)
                        
                        # products
                        c.execute("select count(*) from ob_products where vendor_id=%(user_id)s limit %(quantity)s;", 
                                  {'user_id':rc_user.id,
                                   'quantity':lp})
                        (prod_count, ) = c.fetchone()
                        prod_count = min(prod_count, lp)
                            
                        c.execute("select * from ob_products where vendor_id=%(user_id)s order by date_lastaction desc limit %(quantity)s;", 
                                  {'user_id':rc_user.id,
                                   'quantity':lp})
                            
                        RcProduct = self.get_product_type(c.column_names)
                            
                        prod_chunk = c.fetchmany(size=min(self.PRODUCTS_CHUNK_SIZE, lp))
                        products = []
                        prices = []
                        pictures = []
                        prod_cat = []
                        prod_prg = 0
                        
                        while(len(prod_chunk)>0):
                            
                            # prepare products and related objects for bulk save
                            el_c.execute("select nextval('products_product_id_seq')"+
                                         " from generate_series(1,%(prod_count)s)",
                                         {'prod_count':len(prod_chunk)})
                            
                            for (rc_product, (alloc_id, )) in izip(imap(RcProduct._make, prod_chunk), el_c):
                                
                                if rc_product.id in imported_products_ids:
                                    continue
                                
                                p = {
                                    "id": alloc_id,
                                    #owner
                                    "owner": user,
                                    # desc/summary
                                    "summary": rc_product.name,
                                    "description": product_desc_template\
                                        .render(Context(rc_product._asdict())), #TODO Add all attributes
                                    # TODO caution
                                    "deposit_amount": 0, 
                                    # currency
                                    "currency": rc_user.currency, #TODO handle 0
                                    # addresse =
                                    "address": addr,
                                    # phone =
                                    "phone": user.default_number,
                                    # qty
                                    "quantity": rc_product.qty if rc_product.qty is not None else 0,
                                    # category
                                    "category": DIVERS_CAT, #TODO add real category,
                                    "import_record": ir,
                                    "original_id": rc_product.id,
                                    "created_at":datetime.combine(rc_product.date_added, datetime_orig.time.min),
                                    }
                                
                                product = Product(**p)
                                product.prepare_for_save()
                                products.append(product)
                                
                                prod_cat.append(Product2Category(product=product,
                                                                 category=DIVERS_CAT,
                                                                 site=ELOUE_SITE))
                                
                                if rc_product.price:
                                    prices.append(Price(product_id=alloc_id,
                                                    amount=rc_product.price, 
                                                    currency=rc_user.currency, 
                                                    unit=UNIT.DAY))
                                if rc_product.price_weekly:
                                    prices.append(Price(product_id=alloc_id,
                                                        amount=rc_product.price_weekly, 
                                                        currency=rc_user.currency, 
                                                        unit=UNIT.WEEK))
                                    
                                if rc_product.primary_photo:
                                    pictures.append(Picture(product_id=alloc_id,
                                                    image=rc_product.primary_photo,
                                                    created_at=datetime.now()))


                            # bulk save products and related objects
                            
                            Product.objects.bulk_create(products)
                            Product2Category.objects.bulk_create(prod_cat)
                            ELOUE_SITE.products.add(*products)
                            agency.products.add(*products)
                            Price.objects.bulk_create(prices)
                            Picture.objects.bulk_create(pictures)
                            
                            
                            # get next chunk of products
                            
                            prod_prg = prod_prg + len(prod_chunk)
                            
                            prod_chunk = c.fetchmany(size=min(self.PRODUCTS_CHUNK_SIZE, lp))
                            products = []
                            prod_cat = []
                            prices = []
                            pictures = []
                            self.stdout.write("\rImporting products for user %s: %s / %s" % 
                                              (rc_user.username, prod_prg, prod_count, ), 
                                              ending='\r')
                        
                        prod_total = prod_total + prod_prg
                    
                    ELOUE_SITE.patrons.add(user)
                    ir.patrons.add(user)
                    user_total = user_total + 1
                                    
                chunk = c.fetchmany(size=self.USERS_CHUNK_SIZE)
                users = []
                
            self.stdout.write("\n")
                
            self.stdout.write("\rTotal users imported: %s" % 
              (user_total, ), ending='\n')
                
            self.stdout.write("\rTotal products imported: %s" % 
              (prod_total, ), ending='\n')
            
            if dry_run:
                self.stdout.write(self.style.NOTICE("Dry run was enabled, rolling back."), ending='\n')
                transaction.rollback()
            else:
                self.stdout.write("Committing...", ending='\n')
                transaction.commit()
                
            c.close()
            cnx.close()
            
        except:
            transaction.rollback()
            self.stderr.write("\nGot an error, rolling back. Cause:", ending='\n')
            raise
        
        self.stdout.write("Import done.", ending='\n')
        
        if export_skipped:
            import json
            def date_handler(obj):
                return obj.isoformat() if hasattr(obj, 'isoformat') else obj
            self.stdout.write("Saving skipped objects...", ending='\n')
            f = open("skipped_users.json", "w")
            json.dump(self.skipped_users, f, default=date_handler, indent=1)
            f.close()
            f = open("skipped_products.json", "w")
            json.dump(self.skipped_products, f, default=date_handler, indent=1)
            f.close()
            f = open("skipped_logos.json", "w")
            json.dump(self.skipped_logos, f, default=date_handler, indent=1)
            f.close()
            
        self.stdout.write("Done.", ending='\n')
               
    
    def handle_logos(self, **options):
        
        from threading import Thread
        
        NUM_THREADS = int(options['threads'])
        export_skipped = options['export-skipped']
        
        self.stdout.write("Using %s threads" % NUM_THREADS, ending='\n')
        
        skip_lock = threading.Lock()
        progress_lock = threading.Lock()
        self.progress = 0
   
        def worker(part):
            irs = self.get_record_queryset()        
            for ir in irs:
                pats = ir.patrons.exclude(avatar__isnull=True).exclude(avatar__exact='')
                count = pats.count()
                pats_slice = pats[(count/NUM_THREADS)*part:(count/NUM_THREADS)*(part+1)]
                for pat in pats_slice:
                    try:
                        with progress_lock:
                            self.progress = self.progress + 1
                            self.stdout.write("Logo %5s out of %5s" % (self.progress, count), ending='\r')
                        resp = requests.get(self.LOGOS_URL + pat.avatar.name)
                        resp.raise_for_status()
                        pat.avatar.save('', ContentFile(resp.content))
                    except HTTPError, e:
                        with skip_lock:
                            self.skip_logo(pat, str(e))
        
        for ti in range(NUM_THREADS):
            Thread(target=worker, args=(ti,)).start()
            
        for t in threading.enumerate():
            if t is threading.current_thread():
                continue
            t.join()
            
        self.stdout.write("")
        
        if export_skipped:
            import json
            f = open("skipped_logos.json", "w")
            json.dump(self.skipped_logos, f, indent=1)
            f.close()
        
        self.stdout.write("Done.", ending='\n')
        
  
    def handle_pictures(self, *args, **options):
        from threading import Thread
        
        NUM_THREADS = int(options['threads'])
        export_skipped = options['export-skipped']
        
        self.stdout.write("Using %s threads" % NUM_THREADS, ending='\n')
        
        skip_lock = threading.Lock()
        progress_lock = threading.Lock()
        self.progress = 0
        
        def worker(part):
            storage = Picture._meta.get_field('image').storage
            irs = self.get_record_queryset()        
            for ir in irs:
                pics = Picture.objects.filter(product__import_record=ir)
                count = pics.count()
                pics_slice = pics[(count/NUM_THREADS)*part:(count/NUM_THREADS)*(part+1)]
                for pic in pics_slice:
                    try:
                        name = pic.image.name
                        with progress_lock:
                            self.progress = self.progress + 1
                            self.stdout.write("Picture %7s out of %7s: %50s" % (self.progress, count, name), ending='\r')
                        if storage.exists(pic.image.name):
                            with skip_lock:
                                self.skip_picture(pic, str('already exists'))
                        name = name if name.startswith('http') else self.PICTURES_URL + name
                        resp = requests.get(name)
                        resp.raise_for_status()
                        pic.image.save('', ContentFile(resp.content))
                    except Exception, e:
                        with skip_lock:
                            self.skip_picture(pic, str(e))
        
        for ti in range(NUM_THREADS):
            Thread(target=worker, args=(ti,)).start()
            
        for t in threading.enumerate():
            if t is threading.current_thread():
                continue
            t.join()
        
        self.stdout.write("")
        
        if export_skipped:
            import json
            f = open("skipped_pics.json", "w")
            json.dump(self.skipped_pics, f, indent=1)
            f.close()
        
        self.stdout.write("Done.", ending='\n')
                
    
    def handle_undo(self):
        self.stdout.write("Undoing imports:", ending='\n')
        
        transaction.set_autocommit(False)
        
        try:
            
            irs = self.get_record_queryset()
            
            if not irs.count():
                self.stdout.write("Nothing to undo.", ending='\n')
                return
            
            for ir in irs:
                
                self.stdout.write(ir.imported_at.isoformat(), ending='   ')
                
                # TODO find out why delete trough related manager failed
                prods = Product.objects.filter(import_record=ir)
                pats = Patron.objects.filter(import_record=ir)
                
                self.stdout.write("%6s products" % (prods.count()), ending='   ')
                Price.objects.filter(product__in=prods).delete()
                prods.delete()
                
                self.stdout.write("%6s patrons" % (pats.count()), ending='   ')
                ProAgency.objects.filter(patron__in=pats).delete()
                Address.objects.filter(patron__in=pats).delete()
                PhoneNumber.objects.filter(patron__in=pats).delete()
                pats.delete()
                
                ir.delete()
                
                self.stdout.write("deleted", ending='\n')
            
            self.stdout.write("Committing...", ending='\n')
            transaction.commit()
            
        except:
            transaction.rollback()
            self.stderr.write("\nGot an error, rolling back. Cause:", ending='\n')
            raise
        
        self.stdout.write("Done.", ending='\n')
        
        
    def handle_index(self):
        from products.search_indexes import ProductIndex
        from accounts.search_indexes import PatronIndex
        
        pati = PatronIndex()
        prodi = ProductIndex()
        
        irs = self.get_record_queryset()
        
        if not irs.count():
            self.stdout.write("Nothing to index.", ending='\n')
            return
        
        for ir in irs:
            map(pati.update_object, Patron.objects.filter(import_record=ir))
            map(prodi.update_object, Product.objects.filter(import_record=ir))
            
        self.stdout.write("Done.", ending='\n')
        
        
        