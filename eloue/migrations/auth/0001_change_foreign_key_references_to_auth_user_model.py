# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection
from django.conf import settings
try:
    from django.contrib.auth import get_user_model
    AUTH_USER_MODEL = settings.AUTH_USER_MODEL
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
    AUTH_USER_MODEL = 'auth.User'


class Migration(SchemaMigration):

    depends_on = (
        # We do really depend on the migration which changes the things in accounts/auth
        ('accounts', '0038_django15_new_auth_patron_post'),
        # We also depend on applications which are affected by this migration
        ('announcements', '0001_initial'),
        ('oauth_provider', '0001_initial'),
        ('django_messages', '0001_initial'),
        ('django_lean.experiments', '0001_initial'),
    )

    needed_by = (
        # hook the migration to be automatically applied during update/migration of announcements and oauth_provider apps
        ('announcements', '0002_upgrade_0_2_0'),
        ('oauth_provider', '0002_auto__add_field_consumer_xauth_allowed'),
    )

    def forwards(self, orm):

        # Deleting model 'Message' which has been removed in Django 1.4
        if 'auth_message' in connection.introspection.table_names():
            db.delete_table('auth_message')

        # Replacing foreign key reference to user model for model 'admin.LogEntry'
        db.delete_foreign_key('django_admin_log', 'user_id')
        db.alter_column('django_admin_log', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL]))

        # Replacing foreign key reference to user model for model 'announcements.Announcement'

        db.delete_foreign_key('announcements_announcement', 'creator_id')
        db.alter_column('announcements_announcement', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL]))

        # Replacing foreign key reference to user model for model 'oauth_provider.Consumer'

        db.delete_foreign_key('oauth_provider_consumer', 'user_id')
        db.alter_column('oauth_provider_consumer', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL], null=True, blank=True))

        db.delete_foreign_key('oauth_provider_token', 'user_id')
        db.alter_column('oauth_provider_token', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tokens', to=orm[AUTH_USER_MODEL], null=True, blank=True))

        # Replacing foreign key reference to user model for model 'django_messages.Message'

        db.delete_foreign_key('django_messages_message', 'sender_id')
        db.alter_column('django_messages_message', 'sender_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm[AUTH_USER_MODEL]))

        db.delete_foreign_key('django_messages_message', 'recipient_id')
        db.alter_column('django_messages_message', 'recipient_id', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='received_messages', null=True, to=orm[AUTH_USER_MODEL]))

        # Replacing foreign key reference to user model for model 'experiments..Participant'

        db.delete_foreign_key('experiments_participant', 'user_id')
        db.alter_column('experiments_participant', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL], null=True))

    def backwards(self, orm):
        # We cannot restore reference keys to auth.User by means of Django ORM if it is not the currently used auth model
        if AUTH_USER_MODEL != 'auth.User':
            if not settings.DEBUG:
                raise RuntimeError('Cannot reverse this migration.')

    models = {
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
        AUTH_USER_MODEL: {
            'Meta': {'object_name': User.__name__, 'db_table': "'%s'" % User._meta.db_table,},
            User._meta.pk.attname: ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'%s'" % User._meta.pk.column}),
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
    }
 
    complete_apps = ['auth']
