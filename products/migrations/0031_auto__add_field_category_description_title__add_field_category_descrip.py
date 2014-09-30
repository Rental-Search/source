# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

try:
    from django_fsm import FSMField
    FSMField = 'django_fsm.FSMField'
except ImportError:
    from django_fsm.db.fields.fsmfield import FSMField
    FSMField = 'django_fsm.db.fields.fsmfield.FSMField'


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Category.title'
        db.add_column(u'products_category', 'title',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Category.description'
        db.add_column(u'products_category', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Category.header'
        db.add_column(u'products_category', 'header',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Category.footer'
        db.add_column(u'products_category', 'footer',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Category.title'
        db.delete_column(u'products_category', 'title')

        # Deleting field 'Category.description'
        db.delete_column(u'products_category', 'description')

        # Deleting field 'Category.header'
        db.delete_column(u'products_category', 'header')

        # Deleting field 'Category.footer'
        db.delete_column(u'products_category', 'footer')


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
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
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
            'category': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'description_instance'", 'unique': 'True', 'to': u"orm['products.Category']"}),
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
            'state': (FSMField, [], {'default': "'authorizing'", 'max_length': '50'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['products']
