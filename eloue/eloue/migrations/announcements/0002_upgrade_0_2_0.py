# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
try:
    from django.contrib.auth import get_user_model
    from django.conf import settings
    AUTH_USER_MODEL = settings.AUTH_USER_MODEL
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
    AUTH_USER_MODEL = 'auth.User'


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Dismissal'
        db.create_table('announcements_dismissal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='announcement_dismissals', to=orm[AUTH_USER_MODEL])),
            ('announcement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dismissals', to=orm['announcements.Announcement'])),
            ('dismissed_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('announcements', ['Dismissal'])

        # Adding field 'Announcement.dismissal_type'
        db.add_column('announcements_announcement', 'dismissal_type',
                      self.gf('django.db.models.fields.IntegerField')(default=2),
                      keep_default=False)

        # Adding field 'Announcement.publish_start'
        db.add_column('announcements_announcement', 'publish_start',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Announcement.publish_end'
        db.add_column('announcements_announcement', 'publish_end',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):

        # Deleting model 'Dismissal'
        db.delete_table('announcements_dismissal')

        # Deleting field 'Announcement.dismissal_type'
        db.delete_column('announcements_announcement', 'dismissal_type')

        # Deleting field 'Announcement.publish_start'
        db.delete_column('announcements_announcement', 'publish_start')

        # Deleting field 'Announcement.publish_end'
        db.delete_column('announcements_announcement', 'publish_end')

    models = {
        u'announcements.announcement': {
            'Meta': {'object_name': 'Announcement'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s']" % AUTH_USER_MODEL}),
            'dismissal_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publish_start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'site_wide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'announcements.dismissal': {
            'Meta': {'object_name': 'Dismissal'},
            'announcement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dismissals'", 'to': u"orm['announcements.Announcement']"}),
            'dismissed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'announcement_dismissals'", 'to': u"orm['%s']" % AUTH_USER_MODEL})
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
        }
    }

    complete_apps = ['announcements']
