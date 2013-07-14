# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GlacierVault'
        db.create_table(u'glacier_backup_glaciervault', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('glacier_backup', ['GlacierVault'])

        # Adding model 'GlacierBackup'
        db.create_table(u'glacier_backup_glacierbackup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('backup_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('vault', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['glacier_backup.GlacierVault'])),
            ('path_origin', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('glacier_backup', ['GlacierBackup'])

        # Adding model 'GlacierLog'
        db.create_table(u'glacier_backup_glacierlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('glacier_backup', ['GlacierLog'])


    def backwards(self, orm):
        # Deleting model 'GlacierVault'
        db.delete_table(u'glacier_backup_glaciervault')

        # Deleting model 'GlacierBackup'
        db.delete_table(u'glacier_backup_glacierbackup')

        # Deleting model 'GlacierLog'
        db.delete_table(u'glacier_backup_glacierlog')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['glacier_backup']