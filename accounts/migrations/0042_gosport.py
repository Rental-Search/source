# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        eloue_siteid = 1
        gosport_site_id = 13
        site = orm['sites.Site'].objects.get(pk=gosport_site_id)
        for user in orm.Patron.objects.filter(sites__id=eloue_siteid):
            user.sites.add(site)

    def backwards(self, orm):
        "Write your backwards methods here."
        gosport_site_id = 13
        site = orm['sites.Site'].objects.get(pk=gosport_site_id)
        for user in orm.Patron.objects.filter(sites__id=gosport_site_id):
            user.sites.remove(site)

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
            'state': ('django_fsm.FSMField', [], {'default': "'unpaid'", 'max_length': '50'}),
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
            'default_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.Address']"}),
            'default_number': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.PhoneNumber']"}),
            'drivers_license_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'drivers_license_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'godfather_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'hobby': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'iban': ('django_iban.fields.IBANField', [], {'max_length': '34', 'blank': 'True'}),
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
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'products.product': {
            'Meta': {'object_name': 'Product'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.Address']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['products.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deposit_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['accounts.Patron']"}),
            'payment_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'phone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['accounts.PhoneNumber']"}),
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
        u'products.producttopposition': {
            'Meta': {'object_name': 'ProductTopPosition'},
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['products.Product']"}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['accounts']
    symmetrical = True
