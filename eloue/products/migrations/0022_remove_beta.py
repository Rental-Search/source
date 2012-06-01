# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.contrib import sites, admin
from eloue.accounts.models import Patron

class FakeAdmin(object):
    def has_perm(self, perm): return True

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        to_delete, perms_needed = admin.util.get_deleted_objects(
            sites.models.Site.objects.filter(domain='beta.e-loue.com'),
            None, FakeAdmin(), admin.site
        )
        assert len(to_delete)==1, 'Warning, other object than Site(\'beta.e-loue.com\' would get deleted. Exit.'
        sites.models.Site.objects.get(domain='beta.e-loue.com').delete()

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sites']
