from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db import connection

import mysql.connector

from accounts.models import Patron, PhoneNumber, Address, ProAgency
from products.models import Product, Category, Price
from collections import namedtuple
from itertools import imap, izip
from accounts.choices import PHONE_TYPES
import signal
from optparse import make_option
from django.template import Template, Context
from products.choices import UNIT


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

    # Patron.origin value 
    ORIGIN = "rentalcompare.com"

    # Product descriptions will be buildt with this template
    PRODUCT_DESC_TEMPLATE=\
"""
{{ description }}

{% if width %}
Width: {{ width }}
{% endif %}
{% if height %}
Height: {{ height }}
{% endif %}
{% if length %}
Length: {{ length }}
{% endif %}
{% if weight %}
Weight: {{ weight }}
{% endif %}
"""

    option_list = BaseCommand.option_list + (
        make_option('--dryrun',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Roll back all changes after command completion'),
        make_option('--export-skipped',
            action='store_true',
            dest='export-skipped',
            default=False,
            help='Export all skipped objects to a .json file'),                                             
        )
    
    def __init__(self):
        BaseCommand.__init__(self)
        self.skipped_users = []
        self.skipped_products = []
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
    
    
    def handle_interrupt(self, signal, frame):
        raise CommandError("Aborted by user")
    
    
    def handle(self, *args, **options):
        
        credentials = {
                       'user': 'root', 
                       'database': 'rentalcompare', 
                       'password': 'root'}
        
        dry_run = options['dryrun']
        export_skipped = options['export-skipped']
        
        user_prg = 0
        prod_prg = 0
        
        slug_attempt = 0
        
        DIVERS_CAT = Category.objects.get(slug="divers");
        
        product_desc_template = Template(self.PRODUCT_DESC_TEMPLATE)
        
        transaction.set_autocommit(False)

        try:
            cnx = mysql.connector.connect(**credentials)
            c = cnx.cursor()
        except:
            self.stderr.write("Could not establish connection "
                               +"to the rentalcompare database. Cause:")
            raise
        
        el_c = connection.cursor()
        
        try:
            
            c.execute("select count(*) from ob_users;")
            (user_count, ) = c.fetchone()
            
            self.stdout.write("Importing %s users" % (user_count, ))
            
            c.execute("select * from ob_users;")
            RcUser = self.get_user_type(c.column_names)
            
            chunk = c.fetchmany(size=self.USERS_CHUNK_SIZE)
            
            while len(chunk)>0:
                
                for rc_user in imap(RcUser._make, chunk):
                    
                    self.stdout.write("Importing user %5s out of %5s : %-50s" % \
                                      (user_prg, user_count, rc_user.username, ), ending='\r')
                    
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
                         'email': rc_user.email,
                         'first_name': rc_user.display_name[:30],
                         'last_name': rc_user.lastname[:30],
                         'url': rc_user.website if rc_user.website is not None else "",
                         'about': rc_user.about_me,
                         'origin': self.ORIGIN,
                         'original_id': rc_user.id,
                         # logo/userpic
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
                    
                    if Patron.objects.exists(username=rc_user.username):
                        # TODO generate new login properly
                        u['username'] = u['username'] + "_1"
                    
                    user = Patron(**u)
                    
                    user.init_slug()
                    
                    slug_attempt = 0
                    while Patron.objects.exists(slug=user.slug):
                        # TODO generate new slug properly
                        slug_attempt = slug_attempt + 1
                        user.slug = user.slug + "-" + str(slug_attempt)
                                        
                    if Patron.objects.exists(email=rc_user.email):
                        # TODO do not skip existing emails
                        self.skip_user(rc_user, "email exists")
                        continue
                    
                    user.slug = user.slug[:50]
                    
                    if rc_user.phonenumber is not None:
                        user.default_number = PhoneNumber(patron=user,
                                       number=rc_user.phonenumber,
                                       kind=PHONE_TYPES.OTHER)
                    
                    user.save()
                    #TODO index users
                    
                    # user address
                    if rc_user.has_address:
                        # TODO refactor condition
                        addr = rc_user.make_address(user)
                        addr.save()
                    
                    if rc_user.level == "vendor":

                        # boutique(s)
                        # TODO refactor into User.build_boutique
                        agency = ProAgency.objects.create(patron=user,
                                                 name=rc_user.company[:50],
                                                 phone_number=user.default_number,
                                                 address1=addr.address1,
                                                 address2=addr.address2,
                                                 zipcode=addr.zipcode,
                                                 city=addr.city,
                                                 state=addr.state,
                                                 country=addr.country)
                        
                        # products
                        c.execute("select count(*) from ob_products where vendor_id=%(user_id)s;", 
                                  {'user_id':rc_user.id})
                        (prod_count, ) = c.fetchone()
                            
                        c.execute("select * from ob_products where vendor_id=%(user_id)s;", 
                                  {'user_id':rc_user.id})
                            
                        RcProduct = self.get_product_type(c.column_names)
                            
                        prod_chunk = c.fetchmany(size=self.PRODUCTS_CHUNK_SIZE)
                        products = []
                        prices = []
                        prod_prg = 0
                        
                        while(len(prod_chunk)>0):
                            
                            el_c.execute("select nextval('products_product_id_seq')"+
                                         " from generate_series(1,%(prod_count)s)",
                                         {'prod_count':len(prod_chunk)})
                            
                            for (rc_product, (alloc_id, )) in izip(imap(RcProduct._make, prod_chunk), el_c):
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
                                    "category": DIVERS_CAT, #TODO add real category
                                    }
                                
                                #TODO prices
                                product = Product(**p)
                                product.prepare_for_save()
                                products.append(product)
                                prices.append(Price(product_id=alloc_id,
                                                    amount=rc_product.price, 
                                                    currency=rc_user.currency, 
                                                    unit=UNIT.DAY))
                                if rc_product.price_weekly is not None:
                                    prices.append(Price(product_id=alloc_id,
                                                        amount=rc_product.price_weekly, 
                                                        currency=rc_user.currency, 
                                                        unit=UNIT.WEEK))
                                
                            Product.objects.bulk_create(products)
                            agency.products.add(*products)
                            Price.objects.bulk_create(prices)
                            #TODO index products
    
                            prod_prg = prod_prg + len(prod_chunk)
                            prod_chunk = c.fetchmany(size=self.PRODUCTS_CHUNK_SIZE)
                            products = []
                            prices = []
                            self.stdout.write("\rImporting products for user %s: %s / %s" % 
                                              (rc_user.username, prod_prg, prod_count, ), 
                                              ending='\r')
                              
                    user_prg = user_prg + 1
                    
                
                self.stdout.write("\n")
                
                chunk = c.fetchmany(size=self.USERS_CHUNK_SIZE)
                users = []
                
            
            if dry_run:
                self.stdout.write(self.style.NOTICE("Dry run was enabled, rolling back."), ending='\n')
                transaction.rollback()
            else:
                transaction.commit()
            
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

        self.stdout.write("Done.", ending='\n')
            
                
    def undo(self):
        #TODO
        pass
                
            
        
        
        