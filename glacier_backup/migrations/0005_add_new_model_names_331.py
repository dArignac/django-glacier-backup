# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Vault'
        db.create_table(u'glacier_backup_vault', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('glacier_backup', ['Vault'])

        # Adding model 'Archive'
        db.create_table(u'glacier_backup_archive', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('backup_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('vault', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['glacier_backup.Vault'])),
            ('path_origin', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('glacier_backup', ['Archive'])


    def backwards(self, orm):
        # Deleting model 'Vault'
        db.delete_table(u'glacier_backup_vault')

        # Deleting model 'Archive'
        db.delete_table(u'glacier_backup_archive')


    models = {
        'glacier_backup.archive': {
            'Meta': {'object_name': 'Archive'},
            'backup_id': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path_origin': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vault': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['glacier_backup.Vault']"})
        },
        'glacier_backup.glacierbackup': {
            'Meta': {'object_name': 'GlacierBackup'},
            'backup_id': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path_origin': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vault': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['glacier_backup.GlacierVault']"})
        },
        'glacier_backup.glaciervault': {
            'Meta': {'object_name': 'GlacierVault'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'glacier_backup.vault': {
            'Meta': {'object_name': 'Vault'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['glacier_backup']