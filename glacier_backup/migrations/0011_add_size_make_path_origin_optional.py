# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Archive.size'
        db.add_column(u'glacier_backup_archive', 'size',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'Archive.path_origin'
        db.alter_column(u'glacier_backup_archive', 'path_origin', self.gf('django.db.models.fields.CharField')(max_length=512, null=True))

    def backwards(self, orm):
        # Deleting field 'Archive.size'
        db.delete_column(u'glacier_backup_archive', 'size')


        # Changing field 'Archive.path_origin'
        db.alter_column(u'glacier_backup_archive', 'path_origin', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=512))

    models = {
        'glacier_backup.archive': {
            'Meta': {'object_name': 'Archive'},
            'backup_id': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path_origin': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vault': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['glacier_backup.Vault']"})
        },
        u'glacier_backup.archiveretrievaljob': {
            'Meta': {'object_name': 'ArchiveRetrievalJob'},
            'archive_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date_completion': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'date_creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'request_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vault': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['glacier_backup.Vault']"})
        },
        u'glacier_backup.inventoryretrievaljob': {
            'Meta': {'object_name': 'InventoryRetrievalJob'},
            'date_completion': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'date_creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'request_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vault': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['glacier_backup.Vault']"})
        },
        'glacier_backup.vault': {
            'Meta': {'object_name': 'Vault'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['glacier_backup']