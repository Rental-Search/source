# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BillingPhoneNotification'
        db.create_table('accounts_billingphonenotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phonenotification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.PhoneNotificationHistory'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Billing'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('accounts', ['BillingPhoneNotification'])

        # Adding model 'BillingProductHighlight'
        db.create_table('accounts_billingproducthighlight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('producthighlight', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['products.ProductHighlight'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Billing'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('accounts', ['BillingProductHighlight'])

        # Adding model 'ProPackage'
        db.create_table('accounts_propackage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('maximum_items', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('valid_from', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('valid_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['ProPackage'])

        # Adding unique constraint on 'ProPackage', fields ['maximum_items', 'valid_until']
        db.create_unique('accounts_propackage', ['maximum_items', 'valid_until'])

        # Adding model 'Subscription'
        db.create_table('accounts_subscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron'])),
            ('propackage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.ProPackage'])),
            ('subscription_started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subscription_ended', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['Subscription'])

        # Adding model 'EmailNotificationHistory'
        db.create_table('accounts_emailnotificationhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('notification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.EmailNotification'])),
        ))
        db.send_create_signal('accounts', ['EmailNotificationHistory'])

        # Adding model 'BillingEmailNotification'
        db.create_table('accounts_billingemailnotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('emailnotification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.EmailNotificationHistory'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Billing'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('accounts', ['BillingEmailNotification'])

        # Adding model 'PhoneNotification'
        db.create_table('accounts_phonenotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron'])),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('ended_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('accounts', ['PhoneNotification'])

        # Adding model 'BillingHistory'
        db.create_table('accounts_billinghistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Billing'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('succeeded', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('accounts', ['BillingHistory'])

        # Adding model 'BillingProductTopPosition'
        db.create_table('accounts_billingproducttopposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('producttopposition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['products.ProductTopPosition'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Billing'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('accounts', ['BillingProductTopPosition'])

        # Adding model 'BillingSubscription'
        db.create_table('accounts_billingsubscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Subscription'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Billing'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('accounts', ['BillingSubscription'])

        # Adding model 'PhoneNotificationHistory'
        db.create_table('accounts_phonenotificationhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('notification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.PhoneNotification'])),
        ))
        db.send_create_signal('accounts', ['PhoneNotificationHistory'])

        # Adding model 'EmailNotification'
        db.create_table('accounts_emailnotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron'])),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('ended_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('accounts', ['EmailNotification'])

        # Adding model 'Billing'
        db.create_table('accounts_billing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('patron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Patron'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('state', self.gf('django.db.models.fields.CharField')(default='unpaid', max_length=50)),
            ('total_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_tva', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('accounts', ['Billing'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ProPackage', fields ['maximum_items', 'valid_until']
        db.delete_unique('accounts_propackage', ['maximum_items', 'valid_until'])

        # Deleting model 'BillingPhoneNotification'
        db.delete_table('accounts_billingphonenotification')

        # Deleting model 'BillingProductHighlight'
        db.delete_table('accounts_billingproducthighlight')

        # Deleting model 'ProPackage'
        db.delete_table('accounts_propackage')

        # Deleting model 'Subscription'
        db.delete_table('accounts_subscription')

        # Deleting model 'EmailNotificationHistory'
        db.delete_table('accounts_emailnotificationhistory')

        # Deleting model 'BillingEmailNotification'
        db.delete_table('accounts_billingemailnotification')

        # Deleting model 'PhoneNotification'
        db.delete_table('accounts_phonenotification')

        # Deleting model 'BillingHistory'
        db.delete_table('accounts_billinghistory')

        # Deleting model 'BillingProductTopPosition'
        db.delete_table('accounts_billingproducttopposition')

        # Deleting model 'BillingSubscription'
        db.delete_table('accounts_billingsubscription')

        # Deleting model 'PhoneNotificationHistory'
        db.delete_table('accounts_phonenotificationhistory')

        # Deleting model 'EmailNotification'
        db.delete_table('accounts_emailnotification')

        # Deleting model 'Billing'
        db.delete_table('accounts_billing')


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
        'accounts.billing': {
            'Meta': {'object_name': 'Billing'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'emailnotifications': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.EmailNotificationHistory']", 'through': "orm['accounts.BillingEmailNotification']", 'symmetrical': 'False'}),
            'highlights': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['products.ProductHighlight']", 'through': "orm['accounts.BillingProductHighlight']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Patron']"}),
            'phonenotifications': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.PhoneNotificationHistory']", 'through': "orm['accounts.BillingPhoneNotification']", 'symmetrical': 'False'}),
            'plans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.Subscription']", 'through': "orm['accounts.BillingSubscription']", 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'unpaid'", 'max_length': '50'}),
            'toppositions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['products.ProductTopPosition']", 'through': "orm['accounts.BillingProductTopPosition']", 'symmetrical': 'False'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_tva': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        'accounts.billingemailnotification': {
            'Meta': {'object_name': 'BillingEmailNotification'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Billing']"}),
            'emailnotification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.EmailNotificationHistory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        'accounts.billinghistory': {
            'Meta': {'object_name': 'BillingHistory'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Billing']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'succeeded': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'accounts.billingphonenotification': {
            'Meta': {'object_name': 'BillingPhoneNotification'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Billing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phonenotification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.PhoneNotificationHistory']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        'accounts.billingproducthighlight': {
            'Meta': {'object_name': 'BillingProductHighlight'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Billing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'producthighlight': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['products.ProductHighlight']"})
        },
        'accounts.billingproducttopposition': {
            'Meta': {'object_name': 'BillingProductTopPosition'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Billing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'producttopposition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['products.ProductTopPosition']"})
        },
        'accounts.billingsubscription': {
            'Meta': {'object_name': 'BillingSubscription'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Billing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Subscription']"})
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
        'accounts.emailnotification': {
            'Meta': {'object_name': 'EmailNotification'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Patron']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'accounts.emailnotificationhistory': {
            'Meta': {'object_name': 'EmailNotificationHistory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.EmailNotification']"}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.ProPackage']", 'through': "orm['accounts.Subscription']", 'symmetrical': 'False'}),
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
        'accounts.phonenotification': {
            'Meta': {'object_name': 'PhoneNotification'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Patron']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'accounts.phonenotificationhistory': {
            'Meta': {'object_name': 'PhoneNotificationHistory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.PhoneNotification']"}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
        'products.producthighlight': {
            'Meta': {'object_name': 'ProductHighlight'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['products.Product']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'products.producttopposition': {
            'Meta': {'object_name': 'ProductTopPosition'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['products.Product']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['accounts']
