import logging
import os

from django.core.management.base import BaseCommand, CommandError

from glacier_backup import app_settings as settings
from glacier_backup.aws import Glacier
from glacier_backup.models import Archive, Vault


class Command(BaseCommand):
    args = '<path-to-backup-file> <backup-title> <vault-name>'
    help = 'Creates an AWS Glacier backup for the given file.'

    def handle(self, *args, **options):
        logger = logging.getLogger('glacier_backup')

        ### check prerequisites:
        # given arguments
        if len(args) != 3:
            raise CommandError('Please enter the correct number of arguments: %s' % self.args)

        # set settings
        if len(settings.AWS_ACCESS_KEY_ID) < 5 or len(settings.AWS_SECRET_ACCESS_KEY) < 5 or len(settings.AWS_REGION_NAME) < 5:
            raise CommandError('At least one AWS setting is wrong!')

        # check if the file exists
        path_source_file = args[0]
        if not os.path.isfile(path_source_file):
            raise CommandError('The given file "%s" does not exist or is not a file!' % path_source_file)

        # backup title
        backup_title = args[1]
        if len(backup_title) < 5:
            raise CommandError('Please enter a more specific backup title than just "%s"' % backup_title)

        # vault existence
        try:
            vault = Vault.objects.get(name=args[2])
        except Vault.DoesNotExist:
            raise CommandError('A vault with the name "%s" does not exist!' % args[2])

        # create the db instance if not already there
        (archive, created,) = Archive.objects.get_or_create(
            title=backup_title,
            vault=vault,
            path_origin=path_source_file,
            status=0,
        )

        if not created:
            raise CommandError('Backup with this parameters already exists!')

        # log something
        logger.info('Trying to push "%(filename)s" to vault "%(vault)s" as "%(title)s"...' % {
            'filename': path_source_file,
            'vault': vault.name,
            'title': backup_title,
        })

        try:
            file_obj = open(path_source_file)

            archive.backup_id = Glacier().upload_archive_to_vault(
                str(vault.name),
                os.path.basename(path_source_file),
                file_obj,
                backup_title,
            )
            archive.status = 1
            archive.save()

            file_obj.close()

            logger.info('Successfully uploaded backup "%(title)s" with PK %(pk)s' % {
                'title': archive.title,
                'pk': archive.pk,
            })
        except Exception as e:
            logger.error('Error occurred for current backup:')
            logger.exception(e)
            archive.status = 2
            archive.save()
