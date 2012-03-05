# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RealEstateProduct'
        db.create_table('products_realestateproduct', (
            ('product_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['products.Product'], unique=True, primary_key=True)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')()),
            ('private_life', self.gf('django.db.models.fields.IntegerField')()),
            ('chamber_number', self.gf('django.db.models.fields.IntegerField')()),
            ('rules', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('air_conditioning', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('breakfast', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('balcony', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lockable_chamber', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('towel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lift', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('family_friendly', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gym', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accessible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('heating', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('jacuzzi', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('chimney', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('internet_access', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('kitchen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('smoking_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ideal_for_events', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tv', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('washing_machine', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tumble_dryer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('computer_with_internet', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('products', ['RealEstateProduct'])

        # Adding model 'CarProduct'
        db.create_table('products_carproduct', (
            ('product_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['products.Product'], unique=True, primary_key=True)),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('seat_number', self.gf('django.db.models.fields.IntegerField')()),
            ('door_number', self.gf('django.db.models.fields.IntegerField')()),
            ('fuel', self.gf('django.db.models.fields.IntegerField')()),
            ('transmission', self.gf('django.db.models.fields.IntegerField')()),
            ('mileage', self.gf('django.db.models.fields.IntegerField')()),
            ('consumption', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('air_conditioning', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('power_steering', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cruise_control', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gps', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('baby_seat', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('roof_box', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bike_rack', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('snow_tires', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('snow_chains', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ski_rack', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cd_player', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('audio_input', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tax_horsepower', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('licence_plate', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('first_registration_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('products', ['CarProduct'])


    def backwards(self, orm):
        
        # Deleting model 'RealEstateProduct'
        db.delete_table('products_realestateproduct')

        # Deleting model 'CarProduct'
        db.delete_table('products_carproduct')


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
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'affiliate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'civility': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'customers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.Patron']", 'symmetrical': 'False'}),
            'default_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['accounts.Address']"}),
            'hobby': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'is_professional': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'is_subscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.Language']", 'symmetrical': 'False', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {}),
            'new_messages_alerted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'paypal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'patrons'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'work': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'})
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
        'django_messages.message': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': "orm['django_messages.Message']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'recipient_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'replied_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': "orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'products.alert': {
            'Meta': {'object_name': 'Alert'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerts'", 'to': "orm['accounts.Address']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerts'", 'to': "orm['accounts.Patron']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'alerts'", 'symmetrical': 'False', 'to': "orm['sites.Site']"})
        },
        'products.answer': {
            'Meta': {'object_name': 'Answer'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['products.Question']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'products.carproduct': {
            'Meta': {'object_name': 'CarProduct', '_ormbases': ['products.Product']},
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'audio_input': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'baby_seat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bike_rack': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'cd_player': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'consumption': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'cruise_control': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'door_number': ('django.db.models.fields.IntegerField', [], {}),
            'first_registration_date': ('django.db.models.fields.DateField', [], {}),
            'fuel': ('django.db.models.fields.IntegerField', [], {}),
            'gps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'licence_plate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'mileage': ('django.db.models.fields.IntegerField', [], {}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'power_steering': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['products.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'roof_box': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'seat_number': ('django.db.models.fields.IntegerField', [], {}),
            'ski_rack': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snow_chains': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snow_tires': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tax_horsepower': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'transmission': ('django.db.models.fields.IntegerField', [], {})
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
        'products.categorydescription': {
            'Meta': {'object_name': 'CategoryDescription'},
            'category': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'description'", 'unique': 'True', 'to': "orm['products.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'footer': ('django.db.models.fields.TextField', [], {}),
            'header': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'products.curiosity': {
            'Meta': {'object_name': 'Curiosity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'curiosities'", 'to': "orm['products.Product']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'curiosities'", 'symmetrical': 'False', 'to': "orm['sites.Site']"})
        },
        'products.messagethread': {
            'Meta': {'object_name': 'MessageThread'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_message': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'last_message_in_thread'", 'unique': 'True', 'null': 'True', 'to': "orm['products.ProductRelatedMessage']"}),
            'last_offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'last_offer_in_thread'", 'unique': 'True', 'null': 'True', 'to': "orm['products.ProductRelatedMessage']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': "orm['products.Product']"}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participating_threads'", 'to': "orm['accounts.Patron']"}),
            'recipient_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'initiated_threads'", 'to': "orm['accounts.Patron']"}),
            'sender_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'products.patronreview': {
            'Meta': {'object_name': 'PatronReview'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': "orm['accounts.Patron']"}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'patronreview_reviews'", 'to': "orm['accounts.Patron']"}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'products.picture': {
            'Meta': {'object_name': 'Picture'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'to': "orm['products.Product']"})
        },
        'products.price': {
            'Meta': {'ordering': "['unit']", 'object_name': 'Price'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'ended_at': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['products.Product']"}),
            'started_at': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'})
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
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['accounts.Patron']"}),
            'payment_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'products'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'products.productrelatedmessage': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'ProductRelatedMessage', '_ormbases': ['django_messages.Message']},
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_messages.Message']", 'unique': 'True', 'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'offer_in_message'", 'unique': 'True', 'null': 'True', 'to': "orm['rent.Booking']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': "orm['products.MessageThread']"})
        },
        'products.productreview': {
            'Meta': {'object_name': 'ProductReview'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': "orm['products.Product']"}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productreview_reviews'", 'to': "orm['accounts.Patron']"}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'products.property': {
            'Meta': {'object_name': 'Property'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['products.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'products.propertyvalue': {
            'Meta': {'unique_together': "(('property', 'product'),)", 'object_name': 'PropertyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['products.Product']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['products.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'products.question': {
            'Meta': {'ordering': "('modified_at', 'created_at')", 'object_name': 'Question'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['accounts.Patron']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['products.Product']"}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'products.realestateproduct': {
            'Meta': {'object_name': 'RealEstateProduct', '_ormbases': ['products.Product']},
            'accessible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'balcony': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'breakfast': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'capacity': ('django.db.models.fields.IntegerField', [], {}),
            'chamber_number': ('django.db.models.fields.IntegerField', [], {}),
            'chimney': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'computer_with_internet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'family_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gym': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'heating': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ideal_for_events': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'internet_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jacuzzi': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kitchen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lift': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lockable_chamber': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'private_life': ('django.db.models.fields.IntegerField', [], {}),
            'product_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['products.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'rules': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'smoking_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'towel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tumble_dryer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tv': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'washing_machine': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'rent.booking': {
            'Meta': {'object_name': 'Booking'},
            'borrower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rentals'", 'to': "orm['accounts.Patron']"}),
            'canceled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'contract_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deposit_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'ended_at': ('django.db.models.fields.DateTimeField', [], {}),
            'insurance_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': "orm['accounts.Patron']"}),
            'pay_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'preapproval_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': "orm['products.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bookings'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'authorizing'", 'max_length': '50'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['products']
