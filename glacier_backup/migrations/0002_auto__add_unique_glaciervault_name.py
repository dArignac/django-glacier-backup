# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'GlacierVault', fields ['name']
        db.create_unique(u'glacier_backup_glaciervault', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'GlacierVault', fields ['name']
        db.delete_unique(u'glacier_backup_glaciervault', ['name'])


    models = {
        'glacier_backup.glacierbackup': {
            'Meta': {'object_name': 'GlacierBackup'},
            'backup_id': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path_origin': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vault': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['glacier_backup.GlacierVault']"})
        },
        'glacier_backup.glacierlog': {
            'Meta': {'object_name': 'GlacierLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        'glacier_backup.glaciervault': {
            'Meta': {'object_name': 'GlacierVault'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['glacier_backup']