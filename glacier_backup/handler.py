import logging

from .aws import Glacier, SQS
from .models import Archive, InventoryRetrievalJob
from .utils import create_local_date_from_utc_datetime_without_tzinfo


logger = logging.getLogger('glacier_backup')


class InventoryRetrievalHandler(object):
    """
    Class that handles the inventory retrieval for Glacier vaults.
    """

    def __init__(self, sqs_message, message_dict):
        """
        :param sqs_message: the boto message instance
        :type sqs_message: boto.sqs.message.Message
        :param message_dict: the message from Glacier as dict. It basically looks this way (example for InventoryRetrievalJob):
        {
            "Type" : "Notification",
            "MessageId" : "2211512d-ab72-530c-bb53-1b2fa124b428",
            "TopicArn" : "<settings.AWS_SNS_TOPIC_ARN>",
            "Message" : {
                "Action": "InventoryRetrieval",
                "ArchiveId": null,
                "ArchiveSHA256TreeHash": null,
                "ArchiveSizeInBytes": null,
                "Completed": true,
                "CompletionDate": "2013-05-06T19:44:22.283Z",
                "CreationDate": "2013-05-06T15:44:16.811Z",
                "InventorySizeInBytes": 763,
                "JobDescription": "<InventoryRetrievalJob.description (if set)>",
                "JobId": "<InventoryRetrievalJob.job_id>",
                "RetrievalByteRange": null,
                "SHA256TreeHash": null,
                "SNSTopic": "<settings.AWS_SNS_TOPIC_ARN>",
                "StatusCode": "Succeeded",
                "StatusMessage": "Succeeded",
                "VaultARN": "<ARN of InventoryRetrievalJob.vault>"
            },
            "Timestamp" : "2013-05-06T19:44:22.381Z",
            "SignatureVersion" : "1",
            "Signature" : "<some-signature>",
            "SigningCertURL" : "<some-pem-url>",
            "UnsubscribeURL" : "<some unsubscribe-url>"
        }
        :type message_dict: dict
        """
        # TODO: I don't know what is contained in message if a job failed! Just handling success here and logging the error!

        # just really use the message and leave the rest be
        msg = message_dict['Message']

        # fetch the job for it
        try:
            job = InventoryRetrievalJob.objects.get(job_id=msg['JobId'])
        except InventoryRetrievalJob.DoesNotExist:
            logger.error('Unable to find a job with id "%(job_id)s" for message id "%(message_id)s' % {
                'job_id': msg['JobId'],
                'message_id': message_dict['MessageId'],
            })
            self.__delete_sqs_message(sqs_message, message_dict)
            return

        # if the status is success, update the job and get the job results
        if msg['StatusCode'] == 'Succeeded':
            # get the job output
            inventory = Glacier().get_job_output(str(job.vault.name), str(job.job_id))

            # if the inventory job does not longer exist, mark it this way and delete the sqs message
            if inventory is None:
                logger.info('inventory result for InventoryJob %d does not longer exist' % job.pk)
                # mark job as deleted
                job.mark_as_deleted_on_glacier()
            else:
                if 'ArchiveList' in inventory:
                    self.__synchronize_archives(job.vault, inventory)

                    # mark job as synchronized / handled
                    job.mark_as_result_synchronized()
                else:
                    logger.error('Inventory job result contained no ArchiveList: %s' % inventory)

        # else write a log and set job as failed
        else:
            logger.error('SQS returned unknown StatusCode "%(status_code)s - marking the job (job_id: %(job_id)s) as failed!' % {
                'status_code': msg['StatusCode'],
                'job_id': job.job_id,
            })

            job.mark_as_failed()

        # finally delete the SQS message
        self.__delete_sqs_message(sqs_message, message_dict)

    def __synchronize_archives(self, vault, inventory):
        """
        Synchronizes the Archive objects in database with the given inventory

        :param vault: the vault of the archives
        :type vault: glacier_backup.models.Vault
        :param inventory: the inventory data
        :type inventory: dict
        """
        # will contain the PKs of the archives handled to remove the archives in db that were not handled
        handled_archives = []

        # walk through the inventory
        for aws_archive in inventory['ArchiveList']:
            # try to get this archive from our database
            try:
                archive = Archive.objects.get(vault=vault, backup_id=aws_archive['ArchiveId'])
            except Archive.DoesNotExist:
                # archive does not exist in our database, so create it
                archive = Archive.objects.create(
                    title=aws_archive['ArchiveDescription'],
                    backup_id=aws_archive['ArchiveId'],
                    created=create_local_date_from_utc_datetime_without_tzinfo(aws_archive['CreationDate']),
                    vault=vault,
                    status=1,
                )
            else:
                # the archive already exists, update the size
                archive.size = aws_archive['Size']
                archive.save()

            # mark as handled
            handled_archives.append(archive.pk)

        # mark the archives that remain and were not synced with the appropriate status
        for unfound_archive in Archive.objects.filter(vault=vault).exclude(pk__in=handled_archives):
            unfound_archive.mark_as_not_on_glacier()

    def __delete_sqs_message(self, sqs_message, message_dict):
        """
        Deletes the given message from SQS.
        :param sqs_message: the message class
        :type sqs_message: boto.sqs.message.Message
        :param message_dict: the message as dict
        :type message_dict: dict
        """
        if not SQS().delete_message(sqs_message):
            logger.error('unable to delete message from sqs: %s' % message_dict)
