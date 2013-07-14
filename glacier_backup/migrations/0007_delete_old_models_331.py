# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'GlacierVault'
        db.delete_table(u'glacier_backup_glaciervault')

        # Deleting model 'GlacierBackup'
        db.delete_table(u'glacier_backup_glacierbackup')


    def backwards(self, orm):
        # Adding model 'GlacierVault'
        db.create_table(u'glacier_backup_glaciervault', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal('glacier_backup', ['GlacierVault'])

        # Adding model 'GlacierBackup'
        db.create_table(u'glacier_backup_glacierbackup', (
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('path_origin', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('vault', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['glacier_backup.GlacierVault'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backup_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('glacier_backup', ['GlacierBackup'])


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
        'glacier_backup.vault': {
            'Meta': {'object_name': 'Vault'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['glacier_backup']