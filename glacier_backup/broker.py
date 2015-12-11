"""Contains broker implementations"""

import logging
import json

from . import app_settings as settings
from . import handler


logger = logging.getLogger('glacier_backup_sqs')


class SQSMessageBroker(object):

    """Message broker for SQS received messages."""

    def delegate(self, sqs_message, message_dict):
        """
        Delegates the given message to the appropriate handler of the handler module if there is any.

        :param sqs_message: the boto message instance
        :type sqs_message: boto.sqs.message.RawMessage
        :param message_dict: the message gotten from SQS as dict
        :type message_dict: dict
        :returns: Nothing
        :rtype: None
        """
        # some keys have to be set, will use this three now
        if 'Type' in message_dict and 'TopicArn' in message_dict and 'Message' in message_dict:
            # handle notifications
            if message_dict['Type'] == 'Notification':
                # handle everything that matches the configured SQS TopicARN
                if message_dict['TopicArn'] == settings.AWS_SNS_TOPIC_ARN:
                    # if the message is not yet a dict, do so
                    if type(message_dict['Message'] != 'dict'):
                        try:
                            message_dict['Message'] = json.loads(message_dict['Message'])
                        except ValueError:
                            logger.exception('Unable to transform the "Message" of the message to Python')
                            return

                    try:
                        return getattr(handler, message_dict['Message']['Action'] + 'Handler')(sqs_message, message_dict)
                    except AttributeError:
                        logger.exception('Unable to call a handler class for SQS message')
                        return

        logger.error('Unable to delegate the message: %s', message_dict)
