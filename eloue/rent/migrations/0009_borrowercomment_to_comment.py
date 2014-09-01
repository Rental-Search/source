# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

try:
    from django_fsm import FSMField
    FSMField = 'django_fsm.FSMField'
except ImportError:
    from django_fsm.db.fields.fsmfield import FSMField
    FSMField = 'django_fsm.db.fields.fsmfield.FSMField'


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        db.execute("""
            INSERT INTO rent_comment (booking_id, comment, note, created_at, type)
            (SELECT booking_id, comment, note, created_at, 1 FROM rent_borrowercomment)
        """)

    def backwards(self, orm):
        "Write your backwards methods here."

        db.execute("""
            INSERT INTO rent_borrowercomment (booking_id, comment, note, created_at)
            (SELECT booking_id, comment, note, created_at FROM rent_comment WHERE type = 1)
        """)
        db.execute("DELETE FROM rent_comment WHERE type = 1")
        
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
        u'accounts.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30'})
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
            'state': (FSMField, [], {'default': "'authorizing'", 'max_length': '50'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        u'rent.bookinglog': {
            'Meta': {'object_name': 'BookingLog'},
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rent.Booking']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_state': (FSMField, [], {'max_length': '50'}),
            'target_state': (FSMField, [], {'max_length': '50'})
        },
        u'rent.borrowercomment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'BorrowerComment', '_ormbases': [u'rent.Comment']},
            u'comment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['rent.Comment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'rent.borrowercomment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'BorrowerComment'},
            'booking': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rent.Booking']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'rent.comment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Comment'},
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['rent.Booking']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
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

    complete_apps = ['rent']
    symmetrical = True
