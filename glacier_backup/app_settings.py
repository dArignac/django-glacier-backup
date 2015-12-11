"""Application settings that can be overwritten with Django settings"""

from django.conf import settings


AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_REGION_NAME = getattr(settings, 'AWS_REGION_NAME', 'eu-west-1')
AWS_SQS_QUEUE_URL = getattr(settings, 'AWS_SQS_QUEUE_URL', '')
AWS_SQS_QUEUE_MESSAGE_WAIT_TIME = getattr(settings, 'AWS_SQS_QUEUE_MESSAGE_WAIT_TIME', 5)
AWS_SQS_DEFAULT_MESSAGES_COLLECTED = getattr(settings, 'AWS_SQS_DEFAULT_MESSAGES_COLLECTED', 10)
AWS_SNS_TOPIC_ARN = getattr(settings, 'AWS_SNS_TOPIC_ARN', '')

# add the log config by hand!
# LOGGING = {
#     'handlers': {
#         'glacier_backup_log': {
#             'level': 'INFO',
#             'class': 'logging.handlers.WatchedFileHandler',
#             'filename': '%slogs/glacier_backup.log' % DIR_INSTALL,
#         },
#         'glacier_backup_sqs_log': {
#             'level': 'INFO',
#             'class': 'logging.handlers.WatchedFileHandler',
#             'filename': '%slogs/glacier_backup_sqs.log' % DIR_INSTALL,
#         },
#     },
#     'loggers': {
#         'glacier_backup': {
#             'handlers': ['glacier_backup_log'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#         'glacier_backup_sqs': {
#             'handlers': ['glacier_backup_sqs_log'],
#             'level': 'INFO',
#             'propagate': False,
#         }
#     }
# }
