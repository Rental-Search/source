# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BookingLog'
        db.create_table('rent_bookinglog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('booking', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rent.Booking'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('source_state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(max_length=50)),
            ('target_state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(max_length=50)),
        ))
        db.send_create_signal('rent', ['BookingLog'])

        # Changing field 'Booking.state'
        db.alter_column('rent_booking', 'state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(max_length=50))


    def backwards(self, orm):
        
        # Deleting model 'BookingLog'
        db.delete_table('rent_bookinglog')

        # Changing field 'Booking.state'
        db.alter_column('rent_booking', 'state', self.gf('django.db.models.fields.CharField')(max_length=50))


    models = {
        'accounts.address': {
            'Meta': {'object_name': 'Address'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': "orm['accounts.Patron']"}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9'})
        },
        'accounts.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'accounts.patron': {
            'Meta': {'object_name': 'Patron', '_ormbases': ['auth.User']},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'affiliate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'civility': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'customers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.Patron']", 'symmetrical': 'False'}),
            'date_of_birth': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['accounts.Address']"}),
            'default_number': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['accounts.PhoneNumber']"}),
            'drivers_license_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'drivers_license_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'hobby': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'is_professional': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'is_subscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['accounts.Language']", 'null': 'True', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'new_messages_alerted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'paypal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'place_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rib': ('django.db.models.fields.CharField', [], {'max_length': '23', 'blank': 'True'}),
            'school': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'patrons'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.ProPackage']", 'through': "orm['accounts.Subscription']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'work': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        'accounts.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phones'", 'to': "orm['accounts.Patron']"})
        },
        'accounts.propackage': {
            'Meta': {'ordering': "('-maximum_items',)", 'unique_together': "(('maximum_items', 'valid_until'),)", 'object_name': 'ProPackage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_items': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'valid_from': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'accounts.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Patron']"}),
            'propackage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.ProPackage']"}),
            'subscription_ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subscription_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 18, 9, 34, 538476)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 18, 9, 34, 538367)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'products.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'need_insurance': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'childrens'", 'null': 'True', 'to': "orm['products.Category']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'categories'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'products.product': {
            'Meta': {'object_name': 'Product'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['accounts.Address']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['products.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deposit_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['accounts.Patron']"}),
            'payment_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'products'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'rent.booking': {
            'Meta': {'object_name': 'Booking'},
            'borrower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rentals'", 'to': "orm['accounts.Patron']"}),
            'canceled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'contract_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deposit_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'ended_at': ('django.db.models.fields.DateTimeField', [], {}),
            'insurance_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': "orm['accounts.Patron']"}),
            'pay_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'preapproval_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': "orm['products.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bookings'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'authorizing'", 'max_length': '50'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'rent.bookinglog': {
            'Meta': {'object_name': 'BookingLog'},
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rent.Booking']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'max_length': '50'}),
            'target_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'max_length': '50'})
        },
        'rent.borrowercomment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'BorrowerComment'},
            'booking': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rent.Booking']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'rent.ownercomment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'OwnerComment'},
            'booking': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rent.Booking']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'rent.sinister': {
            'Meta': {'object_name': 'Sinister'},
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinisters'", 'to': "orm['rent.Booking']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinisters'", 'to': "orm['accounts.Patron']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinisters'", 'to': "orm['products.Product']"}),
            'sinister_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['rent']
