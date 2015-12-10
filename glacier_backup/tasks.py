import json
import logging

from . import app_settings as settings
from .aws import SQS
from .broker import SQSMessageBroker

from celery.task import PeriodicTask

from datetime import timedelta

logger = logging.getLogger('glacier_backup_sqs')


class SQSMessageCollector(PeriodicTask):
    """Periodic task calling SQS for new messages."""
    run_every = timedelta(minutes=30)

    def run(self, **kwargs):
        """Calls SQS for messages and delegates them to the MessageBroker"""
        # get some messages...
        sqs_messages = SQS().get_messages(settings.AWS_SQS_DEFAULT_MESSAGES_COLLECTED)
        broker = SQSMessageBroker()

        # log the received messages
        logger.debug('received %d messages from SQS', len(sqs_messages))

        # iterate them...
        for sqs_message in sqs_messages:
            logger.debug(sqs_message.get_body())
            # try to load the message as JSON
            try:
                message_json = json.loads(sqs_message.get_body())
            except ValueError:
                logger.exception('Converting the message to JSON failed')
            else:
                # the broker decide who shall handle the message
                broker.delegate(sqs_message, message_json)
