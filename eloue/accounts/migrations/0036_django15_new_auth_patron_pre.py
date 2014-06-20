# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # phase 1: drop existing foreign key references from all known models to auth.User

        db.delete_foreign_key('contest_gamer', 'patron_id')

        db.delete_foreign_key('payments_slimpaymandateinformation', 'patron_id')

        db.delete_foreign_key('rent_booking', 'borrower_id')
        db.delete_foreign_key('rent_booking', 'owner_id')
        db.delete_foreign_key('rent_sinister', 'patron_id')

        db.delete_foreign_key('products_alert', 'patron_id')
        db.delete_foreign_key('products_patronreview', 'patron_id')
        db.delete_foreign_key('products_patronreview', 'reviewer_id')
        db.delete_foreign_key('products_productreview', 'reviewer_id')
        db.delete_foreign_key('products_product', 'owner_id')
        db.delete_foreign_key('products_question', 'author_id')
        db.delete_foreign_key('products_messagethread', 'sender_id')
        db.delete_foreign_key('products_messagethread', 'recipient_id')

        db.delete_foreign_key('accounts_address', 'patron_id')
        db.delete_foreign_key('accounts_phonenumber', 'patron_id')
        db.delete_foreign_key('accounts_proagency', 'patron_id')
        db.delete_foreign_key('accounts_subscription', 'patron_id')
        db.delete_foreign_key('accounts_phonenotification', 'patron_id')
        db.delete_foreign_key('accounts_emailnotification', 'patron_id')
        db.delete_foreign_key('accounts_billing', 'patron_id')
        db.delete_foreign_key('accounts_creditcard', 'holder_id')
        db.delete_foreign_key('accounts_idnsession', 'user_id')
        db.delete_foreign_key('accounts_facebooksession', 'user_id')
        db.delete_foreign_key('accounts_openingtimes', 'patron_id')
        db.delete_foreign_key('accounts_patron', 'user_ptr_id')
        db.delete_foreign_key('accounts_patron_languages', 'patron_id')
        db.delete_foreign_key('accounts_patron_sites', 'patron_id')
        db.delete_foreign_key('accounts_patron_customers', 'to_patron_id')
        db.delete_foreign_key('accounts_patron_customers', 'from_patron_id')

        # phase 2: change the primary key for accounts.Patron

        db.delete_primary_key('accounts_patron')
        db.rename_column('accounts_patron', 'user_ptr_id', 'id')
        db.create_primary_key('accounts_patron', ['id'])

        # PostgreSQL uses specific 'sequence' objects for auto-incrementing fields (e.g. primary keys)
        # create a new sequence for the accounts.Patron's primary key field 'id'
        db.execute('CREATE SEQUENCE accounts_patron_id_seq')
        # make the 'id' field to own the sequence (means the sequence will be automatically removed after the table/field is dropped)
        db.execute('ALTER SEQUENCE accounts_patron_id_seq OWNED BY accounts_patron.id')
        # set the starting value according to next available value of the auth_user.id's sequence
        db.execute("SELECT setval('accounts_patron_id_seq', nextval('auth_user_id_seq')) FROM accounts_patron")
        # apply accounts_patron.id to use the sequence
        db.execute("ALTER TABLE accounts_patron ALTER COLUMN id SET DEFAULT nextval('accounts_patron_id_seq')")

        # phase 3: create foreign key references from all known models toaccounts.Patron

        db.alter_column('contest_gamer', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))

        db.alter_column('payments_slimpaymandateinformation', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))

        db.alter_column('rent_booking', 'borrower_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rentals', to=orm['accounts.Patron']))
        db.alter_column('rent_booking', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bookings', to=orm['accounts.Patron']))
        db.alter_column('rent_sinister', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sinisters', to=orm['accounts.Patron']))

        db.alter_column('products_alert', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alerts', to=orm['accounts.Patron']))
        db.alter_column('products_patronreview', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reviews', to=orm['accounts.Patron']))
        db.alter_column('products_patronreview', 'reviewer_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='patronreview_reviews', to=orm['accounts.Patron']))
        db.alter_column('products_productreview', 'reviewer_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='productreview_reviews', to=orm['accounts.Patron']))
        db.alter_column('products_product', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='products', to=orm['accounts.Patron']))
        db.alter_column('products_question', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['accounts.Patron']))
        db.alter_column('products_messagethread', 'sender_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='initiated_threads', to=orm['accounts.Patron']))
        db.alter_column('products_messagethread', 'recipient_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participating_threads', to=orm['accounts.Patron']))

        db.alter_column('accounts_address', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addresses', to=orm['accounts.Patron']))
        db.alter_column('accounts_phonenumber', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='phones', to=orm['accounts.Patron']))
        db.alter_column('accounts_proagency', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pro_agencies', to=orm['accounts.Patron']))
        db.alter_column('accounts_subscription', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_phonenotification', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_emailnotification', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_billing', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_creditcard', 'holder_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['accounts.Patron']))
        db.alter_column('accounts_idnsession', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['accounts.Patron']))
        db.alter_column('accounts_facebooksession', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['accounts.Patron']))
        db.alter_column('accounts_openingtimes', 'patron_id', self.gf('django.db.models.fields.related.OneToOneField')(related_name='opening_times', to=orm['accounts.Patron']))

        db.alter_column('accounts_patron_languages', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_patron_sites', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_patron_customers', 'to_patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_patron_customers', 'from_patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))

        # phase 4: introduce fields from auth.User to accounts.Patron

        db.add_column('accounts_patron', 'password',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)
        db.add_column('accounts_patron', 'last_login',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)
        db.add_column('accounts_patron', 'is_superuser',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)
        db.add_column('accounts_patron', 'username',
                      self.gf('django.db.models.fields.CharField')(default='', unique=False, max_length=30),
                      keep_default=False)
        db.add_column('accounts_patron', 'first_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)
        db.add_column('accounts_patron', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)
        db.add_column('accounts_patron', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='', unique=False, max_length=75),
                      keep_default=False)
        db.add_column('accounts_patron', 'is_staff',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)
        db.add_column('accounts_patron', 'is_active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)
        db.add_column('accounts_patron', 'date_joined',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # phase 5: create M2M tables for accounts.Patron

        # Adding M2M table for field groups on 'Patron'
        db.create_table(db.shorten_name('accounts_patron_groups'), (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patron', models.ForeignKey(orm['accounts.patron'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))

        # Adding M2M table for field user_permissions on 'Patron'
        db.create_table(db.shorten_name('accounts_patron_user_permissions'), (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patron', models.ForeignKey(orm['accounts.patron'], null=False)),
            ('permission', models.ForeignKey(orm['auth.permission'], null=False))
        ))

    def backwards(self, orm):

        # Removing M2M table for field groups on 'Patron'
        db.delete_table(db.shorten_name(u'accounts_patron_groups'))

        # Removing M2M table for field user_permissions on 'Patron'
        db.delete_table(db.shorten_name(u'accounts_patron_user_permissions'))

        db.delete_column('accounts_patron', 'password')
        db.delete_column('accounts_patron', 'last_login')
        db.delete_column('accounts_patron', 'is_superuser')
        db.delete_column('accounts_patron', 'username')
        db.delete_column('accounts_patron', 'first_name')
        db.delete_column('accounts_patron', 'last_name')
        db.delete_column('accounts_patron', 'email')
        db.delete_column('accounts_patron', 'is_staff')
        db.delete_column('accounts_patron', 'is_active')
        db.delete_column('accounts_patron', 'date_joined')

        db.delete_foreign_key('contest_gamer', 'patron_id')

        db.delete_foreign_key('payments_slimpaymandateinformation', 'patron_id')

        db.delete_foreign_key('rent_booking', 'borrower_id')
        db.delete_foreign_key('rent_booking', 'owner_id')
        db.delete_foreign_key('rent_sinister', 'patron_id')

        db.delete_foreign_key('products_alert', 'patron_id')
        db.delete_foreign_key('products_patronreview', 'patron_id')
        db.delete_foreign_key('products_patronreview', 'reviewer_id')
        db.delete_foreign_key('products_productreview', 'reviewer_id')
        db.delete_foreign_key('products_product', 'owner_id')
        db.delete_foreign_key('products_question', 'author_id')
        db.delete_foreign_key('products_messagethread', 'sender_id')
        db.delete_foreign_key('products_messagethread', 'recipient_id')

        db.delete_foreign_key('accounts_address', 'patron_id')
        db.delete_foreign_key('accounts_phonenumber', 'patron_id')
        db.delete_foreign_key('accounts_proagency', 'patron_id')
        db.delete_foreign_key('accounts_subscription', 'patron_id')
        db.delete_foreign_key('accounts_phonenotification', 'patron_id')
        db.delete_foreign_key('accounts_emailnotification', 'patron_id')
        db.delete_foreign_key('accounts_billing', 'patron_id')
        db.delete_foreign_key('accounts_creditcard', 'holder_id')
        db.delete_foreign_key('accounts_idnsession', 'user_id')
        db.delete_foreign_key('accounts_facebooksession', 'user_id')
        db.delete_foreign_key('accounts_openingtimes', 'patron_id')
        db.delete_foreign_key('accounts_patron_languages', 'patron_id')
        db.delete_foreign_key('accounts_patron_sites', 'patron_id')
        db.delete_foreign_key('accounts_patron_customers', 'to_patron_id')
        db.delete_foreign_key('accounts_patron_customers', 'from_patron_id')

        db.execute("ALTER TABLE accounts_patron ALTER COLUMN id DROP DEFAULT")
        db.execute('ALTER SEQUENCE accounts_patron_id_seq OWNED BY NONE')
        db.execute("DROP SEQUENCE accounts_patron_id_seq RESTRICT")

        # Changing field 'Patron.id' to 'Patron.user_ptr'
        db.delete_primary_key('accounts_patron')
        db.rename_column('accounts_patron', 'id', 'user_ptr_id')
        db.create_primary_key('accounts_patron', ['user_ptr_id'])

        db.alter_column('accounts_patron', 'user_ptr_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.user']))

        db.alter_column('contest_gamer', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))

        db.alter_column('payments_slimpaymandateinformation', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))

        db.alter_column('rent_booking', 'borrower_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rentals', to=orm['accounts.Patron']))
        db.alter_column('rent_booking', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bookings', to=orm['accounts.Patron']))
        db.alter_column('rent_sinister', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sinisters', to=orm['accounts.Patron']))

        db.alter_column('products_alert', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alerts', to=orm['accounts.Patron']))
        db.alter_column('products_patronreview', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reviews', to=orm['accounts.Patron']))
        db.alter_column('products_patronreview', 'reviewer_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='patronreview_reviews', to=orm['accounts.Patron']))
        db.alter_column('products_productreview', 'reviewer_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='productreview_reviews', to=orm['accounts.Patron']))
        db.alter_column('products_product', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='products', to=orm['accounts.Patron']))
        db.alter_column('products_question', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['accounts.Patron']))
        db.alter_column('products_messagethread', 'sender_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='initiated_threads', to=orm['accounts.Patron']))
        db.alter_column('products_messagethread', 'recipient_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participating_threads', to=orm['accounts.Patron']))

        db.alter_column('accounts_address', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addresses', to=orm['accounts.Patron']))
        db.alter_column('accounts_phonenumber', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='phones', to=orm['accounts.Patron']))
        db.alter_column('accounts_proagency', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pro_agencies', to=orm['accounts.Patron']))
        db.alter_column('accounts_subscription', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_phonenotification', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_emailnotification', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_billing', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_creditcard', 'holder_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['accounts.Patron']))
        db.alter_column('accounts_idnsession', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['accounts.Patron']))
        db.alter_column('accounts_facebooksession', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['accounts.Patron']))
        db.alter_column('accounts_openingtimes', 'patron_id', self.gf('django.db.models.fields.related.OneToOneField')(related_name='opening_times', to=orm['accounts.Patron']))

        db.alter_column('accounts_patron_languages', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_patron_sites', 'patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_patron_customers', 'to_patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))
        db.alter_column('accounts_patron_customers', 'from_patron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron']))

    models = {
        u'accounts.address': {
            'Meta': {'object_name': 'Address'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': u"orm['accounts.Patron']"}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9'})
        },
        u'accounts.billing': {
            'Meta': {'object_name': 'Billing'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_from': ('django.db.models.fields.DateField', [], {}),
            'date_to': ('django.db.models.fields.DateField', [], {}),
            'emailnotifications': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.EmailNotificationHistory']", 'through': u"orm['accounts.BillingEmailNotification']", 'symmetrical': 'False'}),
            'highlights': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['products.ProductHighlight']", 'through': u"orm['accounts.BillingProductHighlight']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Patron']"}),
            'phonenotifications': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.PhoneNotificationHistory']", 'through': u"orm['accounts.BillingPhoneNotification']", 'symmetrical': 'False'}),
            'plans': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.Subscription']", 'through': u"orm['accounts.BillingSubscription']", 'symmetrical': 'False'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unpaid'", 'max_length': '50'}),
            'toppositions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['products.ProductTopPosition']", 'through': u"orm['accounts.BillingProductTopPosition']", 'symmetrical': 'False'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_tva': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        u'accounts.billingemailnotification': {
            'Meta': {'object_name': 'BillingEmailNotification'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Billing']"}),
            'emailnotification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.EmailNotificationHistory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        u'accounts.billinghistory': {
            'Meta': {'ordering': "['date']", 'object_name': 'BillingHistory'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Billing']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'succeeded': ('django.db.models.fields.BooleanField', [], {})
        },
        u'accounts.billingphonenotification': {
            'Meta': {'object_name': 'BillingPhoneNotification'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Billing']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phonenotification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.PhoneNotificationHistory']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        u'accounts.billingproducthighlight': {
            'Meta': {'object_name': 'BillingProductHighlight'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Billing']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'producthighlight': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['products.ProductHighlight']"})
        },
        u'accounts.billingproducttopposition': {
            'Meta': {'object_name': 'BillingProductTopPosition'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Billing']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'producttopposition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['products.ProductTopPosition']"})
        },
        u'accounts.billingsubscription': {
            'Meta': {'object_name': 'BillingSubscription'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Billing']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Subscription']"})
        },
        u'accounts.creditcard': {
            'Meta': {'object_name': 'CreditCard'},
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'expires': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'holder': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['accounts.Patron']", 'unique': 'True', 'null': 'True'}),
            'holder_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keep': ('django.db.models.fields.BooleanField', [], {}),
            'masked_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subscriber_reference': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'accounts.emailnotification': {
            'Meta': {'object_name': 'EmailNotification'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Patron']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'accounts.emailnotificationhistory': {
            'Meta': {'object_name': 'EmailNotificationHistory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.EmailNotification']"}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'accounts.facebooksession': {
            'Meta': {'unique_together': "(('user', 'uid'), ('access_token', 'expires'))", 'object_name': 'FacebookSession'},
            'access_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['accounts.Patron']", 'unique': 'True', 'null': 'True'})
        },
        u'accounts.idnsession': {
            'Meta': {'unique_together': "(('user', 'uid'), ('access_token', 'access_token_secret'))", 'object_name': 'IDNSession'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'access_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['accounts.Patron']", 'unique': 'True', 'null': 'True'})
        },
        u'accounts.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'accounts.openingtimes': {
            'Meta': {'object_name': 'OpeningTimes'},
            'friday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'friday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'friday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'friday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'monday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'monday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'monday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'patron': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'opening_times'", 'unique': 'True', 'to': u"orm['accounts.Patron']"}),
            'saturday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'saturday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'saturday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'saturday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'sunday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'sunday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'sunday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'sunday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'thursday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'thursday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'thursday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'thursday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tuesday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tuesday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tuesday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tuesday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'wednesday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'wednesday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'wednesday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'wednesday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'accounts.patron': {
            'Meta': {'object_name': 'Patron'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'affiliate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'civility': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'customers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.Patron']", 'symmetrical': 'False'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_of_birth': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['accounts.Address']"}),
            'default_number': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['accounts.PhoneNumber']"}),
            'drivers_license_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'drivers_license_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'godfather_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'hobby': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_professional': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_subscribed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['accounts.Language']", 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'new_messages_alerted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'paypal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'place_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rib': ('django.db.models.fields.CharField', [], {'max_length': '23', 'blank': 'True'}),
            'school': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'patrons'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.ProPackage']", 'through': u"orm['accounts.Subscription']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'work': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        u'accounts.patronaccepted': {
            'Meta': {'object_name': 'PatronAccepted'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'patrons_accepted'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"})
        },
        u'accounts.phonenotification': {
            'Meta': {'object_name': 'PhoneNotification'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Patron']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'accounts.phonenotificationhistory': {
            'Meta': {'object_name': 'PhoneNotificationHistory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.PhoneNotification']"}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'accounts.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phones'", 'to': u"orm['accounts.Patron']"})
        },
        u'accounts.proagency': {
            'Meta': {'object_name': 'ProAgency'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pro_agencies'", 'to': u"orm['accounts.Patron']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9'})
        },
        u'accounts.propackage': {
            'Meta': {'ordering': "('-maximum_items',)", 'unique_together': "(('maximum_items', 'valid_until'),)", 'object_name': 'ProPackage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_items': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'valid_from': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'accounts.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'annual_payment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'free': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_free_month': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Patron']"}),
            'payment_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'propackage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.ProPackage']"}),
            'subscription_ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subscription_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contest.gamer': {
            'Meta': {'object_name': 'Gamer'},
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like_facebook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Patron']"})
        },
        u'contest.productgamer': {
            'Meta': {'object_name': 'ProductGamer'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'gamer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contest.Gamer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['products.Product']"})
        },
        u'django_messages.message': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': u"orm['django_messages.Message']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': u"orm['accounts.Patron']"}),
            'recipient_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'replied_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': u"orm['accounts.Patron']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        u'payments.nonpaymentinformation': {
            'Meta': {'object_name': 'NonPaymentInformation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'payments.payboxdirectpaymentinformation': {
            'Meta': {'object_name': 'PayboxDirectPaymentInformation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numappel': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'numauth': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'numtrans': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'payments.payboxdirectpluspaymentinformation': {
            'Meta': {'object_name': 'PayboxDirectPlusPaymentInformation'},
            'creditcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CreditCard']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numappel': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'numtrans': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'payments.paypalpaymentinformation': {
            'Meta': {'object_name': 'PaypalPaymentInformation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pay_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'preapproval_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'payments.slimpaymandateinformation': {
            'Meta': {'object_name': 'SlimPayMandateInformation'},
            'RUM': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mandateFileName': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Patron']"}),
            'signatureDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transactionErrorCode': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'transactionStatus': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'products.alert': {
            'Meta': {'object_name': 'Alert'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerts'", 'to': u"orm['accounts.Address']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerts'", 'to': u"orm['accounts.Patron']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'alerts'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"})
        },
        u'products.answer': {
            'Meta': {'object_name': 'Answer'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['products.Question']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'products.carproduct': {
            'Meta': {'object_name': 'CarProduct', '_ormbases': [u'products.Product']},
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {}),
            'audio_input': ('django.db.models.fields.BooleanField', [], {}),
            'baby_seat': ('django.db.models.fields.BooleanField', [], {}),
            'bike_rack': ('django.db.models.fields.BooleanField', [], {}),
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'cd_player': ('django.db.models.fields.BooleanField', [], {}),
            'consumption': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4', 'null': 'True', 'blank': 'True'}),
            'costs_per_km': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '3', 'blank': 'True'}),
            'cruise_control': ('django.db.models.fields.BooleanField', [], {}),
            'door_number': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'first_registration_date': ('django.db.models.fields.DateField', [], {}),
            'fuel': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'gps': ('django.db.models.fields.BooleanField', [], {}),
            'km_included': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'licence_plate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'mileage': ('django.db.models.fields.IntegerField', [], {'default': '2', 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'power_steering': ('django.db.models.fields.BooleanField', [], {}),
            u'product_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['products.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'roof_box': ('django.db.models.fields.BooleanField', [], {}),
            'seat_number': ('django.db.models.fields.IntegerField', [], {'default': '4', 'null': 'True', 'blank': 'True'}),
            'ski_rack': ('django.db.models.fields.BooleanField', [], {}),
            'snow_chains': ('django.db.models.fields.BooleanField', [], {}),
            'snow_tires': ('django.db.models.fields.BooleanField', [], {}),
            'tax_horsepower': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'transmission': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'})
        },
        u'products.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'need_insurance': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'childrens'", 'null': 'True', 'to': u"orm['products.Category']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'category_product'", 'unique': 'True', 'null': 'True', 'to': u"orm['products.Product']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'categories'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'products.categorydescription': {
            'Meta': {'object_name': 'CategoryDescription'},
            'category': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'description'", 'unique': 'True', 'to': u"orm['products.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'footer': ('django.db.models.fields.TextField', [], {}),
            'header': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'products.curiosity': {
            'Meta': {'object_name': 'Curiosity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'curiosities'", 'to': u"orm['products.Product']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'curiosities'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"})
        },
        u'products.messagethread': {
            'Meta': {'object_name': 'MessageThread'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_message': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'last_message_in_thread'", 'unique': 'True', 'null': 'True', 'to': u"orm['products.ProductRelatedMessage']"}),
            'last_offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'last_offer_in_thread'", 'unique': 'True', 'null': 'True', 'to': u"orm['products.ProductRelatedMessage']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': u"orm['products.Product']"}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participating_threads'", 'to': u"orm['accounts.Patron']"}),
            'recipient_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'initiated_threads'", 'to': u"orm['accounts.Patron']"}),
            'sender_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        u'products.patronreview': {
            'Meta': {'object_name': 'PatronReview'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': u"orm['accounts.Patron']"}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'patronreview_reviews'", 'to': u"orm['accounts.Patron']"}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'products.picture': {
            'Meta': {'object_name': 'Picture'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'to': u"orm['products.Product']"})
        },
        u'products.price': {
            'Meta': {'ordering': "['unit']", 'object_name': 'Price'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'ended_at': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': u"orm['products.Product']"}),
            'started_at': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'})
        },
        u'products.product': {
            'Meta': {'object_name': 'Product'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['accounts.Address']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['products.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deposit_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['accounts.Patron']"}),
            'payment_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'phone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'null': 'True', 'to': u"orm['accounts.PhoneNumber']"}),
            'pro_agencies': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['accounts.ProAgency']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'products'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'products.producthighlight': {
            'Meta': {'object_name': 'ProductHighlight'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['products.Product']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'products.productrelatedmessage': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'ProductRelatedMessage', '_ormbases': [u'django_messages.Message']},
            u'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_messages.Message']", 'unique': 'True', 'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'offer_in_message'", 'unique': 'True', 'null': 'True', 'to': u"orm['rent.Booking']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': u"orm['products.MessageThread']"})
        },
        u'products.productreview': {
            'Meta': {'object_name': 'ProductReview'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': u"orm['products.Product']"}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productreview_reviews'", 'to': u"orm['accounts.Patron']"}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'products.producttopposition': {
            'Meta': {'object_name': 'ProductTopPosition'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['products.Product']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'products.property': {
            'Meta': {'object_name': 'Property'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['products.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'products.propertyvalue': {
            'Meta': {'unique_together': "(('property', 'product'),)", 'object_name': 'PropertyValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['products.Product']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['products.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'products.question': {
            'Meta': {'ordering': "('modified_at', 'created_at')", 'object_name': 'Question'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': u"orm['accounts.Patron']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': u"orm['products.Product']"}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'products.realestateproduct': {
            'Meta': {'object_name': 'RealEstateProduct', '_ormbases': [u'products.Product']},
            'accessible': ('django.db.models.fields.BooleanField', [], {}),
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {}),
            'balcony': ('django.db.models.fields.BooleanField', [], {}),
            'breakfast': ('django.db.models.fields.BooleanField', [], {}),
            'capacity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'chamber_number': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'chimney': ('django.db.models.fields.BooleanField', [], {}),
            'computer_with_internet': ('django.db.models.fields.BooleanField', [], {}),
            'family_friendly': ('django.db.models.fields.BooleanField', [], {}),
            'gym': ('django.db.models.fields.BooleanField', [], {}),
            'heating': ('django.db.models.fields.BooleanField', [], {}),
            'ideal_for_events': ('django.db.models.fields.BooleanField', [], {}),
            'internet_access': ('django.db.models.fields.BooleanField', [], {}),
            'jacuzzi': ('django.db.models.fields.BooleanField', [], {}),
            'kitchen': ('django.db.models.fields.BooleanField', [], {}),
            'lift': ('django.db.models.fields.BooleanField', [], {}),
            'lockable_chamber': ('django.db.models.fields.BooleanField', [], {}),
            'parking': ('django.db.models.fields.BooleanField', [], {}),
            'private_life': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            u'product_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['products.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'rules': ('django.db.models.fields.TextField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'smoking_accepted': ('django.db.models.fields.BooleanField', [], {}),
            'towel': ('django.db.models.fields.BooleanField', [], {}),
            'tumble_dryer': ('django.db.models.fields.BooleanField', [], {}),
            'tv': ('django.db.models.fields.BooleanField', [], {}),
            'washing_machine': ('django.db.models.fields.BooleanField', [], {})
        },
        u'rent.booking': {
            'Meta': {'object_name': 'Booking'},
            'borrower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rentals'", 'to': u"orm['accounts.Patron']"}),
            'canceled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'contract_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deposit_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'ended_at': ('django.db.models.fields.DateTimeField', [], {}),
            'insurance_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': u"orm['accounts.Patron']"}),
            'pay_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'preapproval_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': u"orm['products.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bookings'", 'symmetrical': 'False', 'to': u"orm['sites.Site']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'authorizing'", 'max_length': '50'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        u'rent.bookinglog': {
            'Meta': {'object_name': 'BookingLog'},
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rent.Booking']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'max_length': '50'}),
            'target_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'max_length': '50'})
        },
        u'rent.borrowercomment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'BorrowerComment'},
            'booking': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['rent.Booking']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'rent.ownercomment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'OwnerComment'},
            'booking': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['rent.Booking']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'rent.sinister': {
            'Meta': {'object_name': 'Sinister'},
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinisters'", 'to': u"orm['rent.Booking']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinisters'", 'to': u"orm['accounts.Patron']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinisters'", 'to': u"orm['products.Product']"}),
            'sinister_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['contest', 'payments', 'rent', 'products', 'accounts', 'auth']
