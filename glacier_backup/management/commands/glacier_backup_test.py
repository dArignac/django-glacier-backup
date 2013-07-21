import json

from django.core.management.base import BaseCommand, CommandError

from glacier_backup.aws import SQS
from glacier_backup.tasks import SQSMessageCollector


class Command(BaseCommand):
    """
    Helper command for testing several functionality.
    """

    def handle(self, *args, **options):
        commands = {
            'sqs_query_direct': {
                'help': 'Retrieve the last 10 messages of the configured SNS topic',
                'method': self.sqs_query_direct,
            },
            'sqs_query_task  ': {
                'help': 'Executes the SQSMessageCollector task',
                'method': self.sqs_query_task,
            }
        }

        if len(args) == 0:
            raise CommandError(
                'Please specify a subcommand to run. This can be:\n' + '\n'.join(
                    ['\t%(key)s:\t%(help)s' % {'key': key, 'help': value['help']} for key, value in commands.items()]
                )
            )

        # run the appropriate subcommand
        commands[args[0]]['method']()

    def sqs_query_task(self):
        """
        Executes the SQSMessageCollector tasks (that is a periodic task!)
        """
        SQSMessageCollector().delay()

    def sqs_query_direct(self):
        """
        Queries SQS for the last 10 messages.
        """
        sqs = SQS()
        ms = sqs.get_messages(10)
        if len(ms) > 0:
            body = ms[0].get_body()
            print json.loads(body)
        else:
            print 'No messages found'
