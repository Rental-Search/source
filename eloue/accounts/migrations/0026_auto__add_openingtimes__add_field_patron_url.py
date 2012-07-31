# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'OpeningTimes'
        db.create_table('accounts_openingtimes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patron', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['accounts.Patron'], unique=True)),
            ('monday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('monday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('monday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('monday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('tuesday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('tuesday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('tuesday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('tuesday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('wednesday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('wednesday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('wednesday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('wednesday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('thursday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('thursday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('thursday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('thursday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('friday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('friday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('friday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('friday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('saturday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('saturday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('saturday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('saturday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('sunday_opens', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('sunday_closes', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('sunday_opens_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('sunday_closes_second', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['OpeningTimes'])

        # Adding field 'Patron.url'
        db.add_column('accounts_patron', 'url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'OpeningTimes'
        db.delete_table('accounts_openingtimes')

        # Deleting field 'Patron.url'
        db.delete_column('accounts_patron', 'url')


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
        'accounts.avatar': {
            'Meta': {'object_name': 'Avatar'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'patron': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'avatar_old'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'accounts.creditcard': {
            'Meta': {'object_name': 'CreditCard'},
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'expires': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'holder': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Patron']", 'unique': 'True', 'null': 'True'}),
            'holder_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'masked_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subscriber_reference': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'accounts.facebooksession': {
            'Meta': {'unique_together': "(('user', 'uid'), ('access_token', 'expires'))", 'object_name': 'FacebookSession'},
            'access_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Patron']", 'unique': 'True', 'null': 'True'})
        },
        'accounts.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'accounts.openingtimes': {
            'Meta': {'object_name': 'OpeningTimes'},
            'friday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'friday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'friday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'friday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monday_closes': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'monday_closes_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'monday_opens': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'monday_opens_second': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'patron': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Patron']", 'unique': 'True'}),
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
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'work': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        'accounts.patronaccepted': {
            'Meta': {'object_name': 'PatronAccepted'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'patrons_accepted'", 'symmetrical': 'False', 'to': "orm['sites.Site']"})
        },
        'accounts.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phones'", 'to': "orm['accounts.Patron']"})
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
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['accounts']
