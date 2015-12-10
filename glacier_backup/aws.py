import boto
import boto.sqs

from boto.glacier.exceptions import UnexpectedHTTPResponseError
from boto.sqs.message import RawMessage
from boto.sqs.queue import Queue

from django.core.exceptions import ImproperlyConfigured

from . import app_settings as settings


class EnsureSettingsSetUpMixin(object):
    """Mixin ensuring that the basic AWS settings were configured."""

    def __init__(self):
        """Checks that the basic AWS settings were configured, else raises error."""
        if len(settings.AWS_ACCESS_KEY_ID) == 0:
            raise ImproperlyConfigured('settings.AWS_ACCESS_KEY_ID is not set correctly!')
        if len(settings.AWS_SECRET_ACCESS_KEY) == 0:
            raise ImproperlyConfigured('settings.AWS_SECRET_ACCESS_KEY is not set correctly!')
        if len(settings.AWS_REGION_NAME) == 0:
            raise ImproperlyConfigured('settings.AWS_REGION_NAME is not set correctly!')
        if len(settings.AWS_SQS_QUEUE_URL) == 0:
            raise ImproperlyConfigured('settings.AWS_SQS_QUEUE_URL is not set correctly!')
        if len(settings.AWS_SNS_TOPIC_ARN) == 0:
            raise ImproperlyConfigured('settings.AWS_SNS_TOPIC_ARN is not set correctly!')


class SQS(EnsureSettingsSetUpMixin):
    """A wrapper around Boto's SQS methods to be able to use more natural methods."""

    def __init__(self):
        """Checks that the basic AWS settings were configured, else raises error."""
        # do what mama says
        super(SQS, self).__init__()

        # check SQS Queue URL
        if len(settings.AWS_SQS_QUEUE_URL) == 0:
            raise ImproperlyConfigured('settings.AWS_SQS_QUEUE_URL is not set correctly!')

    def __get_sqs_connection(self):
        """
        Returns a connection to AWS SQS.

        :returns: connection to SQS
        :rtype: boto.sqs.connection.SQSConnection
        """
        return boto.sqs.connect_to_region(
            settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def __get_queue(self):
        """
        Returns the Queue object for the current configuration.

        :return: the Queue
        :rtype: boto.sqs.queue.Queue
        """
        return Queue(connection=self.__get_sqs_connection(), url=settings.AWS_SQS_QUEUE_URL, message_class=RawMessage)

    def get_messages(self, number_messages, visibility_timeout=None, attributes=None, wait_time_seconds=settings.AWS_SQS_QUEUE_MESSAGE_WAIT_TIME):
        """
        Returns the messages in the given queue.

        :param number_messages: number of messages to queue
        :type number_messages: int
        :param visibility_timeout: the VisibilityTimeout for the messages read
        :type visibility_timeout: int
        :param attributes: The name of additional attribute to return with response or All if you want all attributes. The default is to return no additional
                           attributes. Valid values: All SenderId SentTimestamp ApproximateReceiveCount ApproximateFirstReceiveTimestamp
        :type attributes: str
        :param wait_time_seconds: the duration (in seconds) for which the call will wait for a message to arrive in the queue before returning. If a message is
                                  available, the call will return sooner than wait_time_seconds.
        :type wait_time_seconds: int
        :returns: list of messages
        :rtype: list
        """
        # explicitly create the queue to be able to change the message class and get the contents decoded correctly
        return self.__get_queue().get_messages(
            number_messages,
            visibility_timeout=visibility_timeout,
            attributes=attributes,
            wait_time_seconds=wait_time_seconds,
        )

    def delete_message(self, message):
        """
        Deletes the given message on SQS.

        :param message: the message from SQS
        :type message: boto.sqs.message.Message
        :returns: the success
        :rtype: bool
        """
        return self.__get_queue().delete_message(message)


class Glacier(EnsureSettingsSetUpMixin):
    """A wrapper around Boto's Glacier methods to be able to use more natural methods."""

    def __get_glacier_connection(self):
        """
        Returns a connection to AWS Glacier.

        :returns: glacier connection
        :rtype: boto.glacier.layer2.Layer2
        """
        return boto.connect_glacier(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )

    def exists_vault(self, name):
        """
        Checks if a vault with the given name exists.

        :param name: the name of the vault
        :type name: str
        :returns: if vault exists or not
        :rtype: bool
        """
        try:
            return self.__get_glacier_connection().get_vault(name) is not None
        except UnexpectedHTTPResponseError:
            return False

    def initiate_job(self, vault_name, job_data):
        """
        Queues an inventory retrieval or archive retrieval job to the given vault.

        :param vault_name: the name of the vault
        :type vault_name: str
        :param job_data: the request data describing the job
        :type job_data: dict
        :returns: output from AWS, containing "Location", "RequestId" and "JobId": {u'Location': '...', u'RequestId': '...', u'JobId': '...'}
        :rtype: dict
        """
        return self.__get_glacier_connection().layer1.initiate_job(vault_name, job_data)

    def get_job_output(self, vault_name, job_id, byte_range=None):
        """
        Returns the output of the given job within the given vault.

        :param vault_name: the name of the vault the job is within
        :type vault_name: str
        :param job_id: the id of the job
        :type job_id: str
        :param byte_range: a tuple of integers specifying the slice (in bytes) of the archive you want to receive
        :type byte_range: tuple
        :returns: the job content or None
        :rtype: dict
        """
        # try to get the job result. It can happen that the job is already outdated thus the request will throw an exception.
        try:
            return self.__get_glacier_connection().layer1.get_job_output(vault_name, job_id, byte_range)
        except UnexpectedHTTPResponseError:
            return None

    def upload_archive_to_vault(self, vault_name, filename, file_obj, description):
        """
        Uploads the given source file to the vault with the given name using the given archive title.

        :param vault_name: the name of the vault
        :type vault_name: str
        :param filename: the filename to use for the archive
        :type filename: str
        :param file_obj: the file object pointing to the real file
        :type file_obj: file
        :param description: a description for the archive
        :type description: str
        :returns: the archive id
        :rtype: str
        """
        return self.__get_glacier_connection().get_vault(vault_name).create_archive_from_file(
            filename=filename,
            file_obj=file_obj,
            description=description,
        )
