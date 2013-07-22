from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now as tz_aware_now
from django.utils.translation import gettext as _, ugettext_lazy

from glacier_backup.aws import Glacier


class Vault(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,  # as identified by name, there can be only one!
        verbose_name=_('Name'),
    )

    def inventory(self):
        """
        Creates an InventoryRetrievalJob for the vault if there is not already one that has not yet finished.
        """
        job = InventoryRetrievalJob.objects.create(vault=self)
        job.map_job_creation_results(
            Glacier().initiate_job(str(self.name), job.get_job_data())
        )
        job.save()

    def clean(self):
        """
        Ensures the vault really exists on AWS before creating database representation.
        """
        # check if there is an AWS vault with this name
        if not Glacier().exists_vault(str(self.name)):
            raise ValidationError(_('There is no vault with the name "%(vault_name)s" on AWS!') % {'vault_name': self.name})

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label = 'glacier_backup'
        verbose_name = ugettext_lazy('Vault')
        verbose_name_plural = ugettext_lazy('Vaults')


class Archive(models.Model):
    STATUS_CHOICES = (
        (0, _('Initial Status'),),
        (1, _('Uploaded'),),
        (2, _('Failed',)),
        (3, _('Not on Glacier',)),  # status for archives locally in db but not in AWS Glacier
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_('Title'),
    )
    backup_id = models.CharField(
        max_length=512,
        verbose_name=_('Glacier Backup ID'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation Date'),
    )
    vault = models.ForeignKey(Vault)

    path_origin = models.CharField(
        blank=True,
        null=True,
        max_length=512,
        verbose_name=_('Path to original file'),
    )

    size = models.BigIntegerField(
        default=0,
        verbose_name=_('Size in Byte'),
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        verbose_name=_('Status'),
    )

    def get_status_name(self, status_id):
        """
        Returns the name of the given status.
        :param status_id: the status id
        :return: the status name
        :rtype: str
        """
        return dict(self.STATUS_CHOICES)[status_id]

    def mark_as_not_on_glacier(self):
        """
        Marks the archive as not on glacier (found).
        """
        self.status = 3
        self.save()

    def download(self):
        """
        Queues the archive for download.
        """
        # TODO create ArchiveRetrievalJob
        # TODO send job to Glacier
        pass

    def __unicode__(self):
        return u'%(title)s (Vault: %(vault)s) (Status: %(status)s)' % {
            'title': self.title,
            'vault': self.vault.name,
            'status': self.get_status_name(self.status),
        }

    class Meta:
        app_label = 'glacier_backup'
        verbose_name = ugettext_lazy('Archive')
        verbose_name_plural = ugettext_lazy('Archives')


class Job(models.Model):
    STATUS_CHOICES = (
        (0, _('Created'),),
        (1, _('Uploaded'),),
        (2, _('Failed',)),
        (3, _('Deleted on Glacier'),),
        (4, _('Result synchronized'),),
    )

    vault = models.ForeignKey(
        Vault,
        verbose_name=_('Vault'),
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=0,
        verbose_name=_('Status'),
    )

    # e.g. /<some-id>/vaults/<Vault>/jobs/<JobId>
    location = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Location'),
    )

    job_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Job ID'),
    )

    request_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Request ID'),
    )

    description = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Description (optional)')
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation date'),
    )

    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Update date'),
    )

    date_completion = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text=_('Time when AWS Glacier has finished the job'),
        verbose_name=_('Completion date'),
    )

    request_format = 'JSON'

    class Meta:
        abstract = True

    @property
    def sns_topic_arn(self):
        """
        Returns the SNS
        """
        from . import app_settings as settings
        return settings.AWS_SNS_TOPIC_ARN

    def map_job_creation_results(self, results):
        """
        Maps the results of Glacier().initiate_job(...) to the instance.
        :param results: dictionary with AWS results
        :type results: dict
        """
        self.location = results['Location']
        self.request_id = results['RequestId']
        self.job_id = results['JobId']

    def mark_as_failed(self):
        """
        Sets the status of the job to failed.
        """
        self.status = 2
        self.date_completion = tz_aware_now()
        self.save()

    def mark_as_deleted_on_glacier(self):
        """
        If it takes to long to request the job output the job is deleted on Glacier.
        This method then sets the appropriate status for the Job.
        """
        self.status = 3
        self.date_completion = tz_aware_now()
        self.save()

    def mark_as_result_synchronized(self):
        """
        Sets the status of the job to the one that marks that the result of the job has been handled.
        """
        self.status = 4
        self.date_completion = tz_aware_now()
        self.save()

    def __get_specific_job_data(self):
        """
        Returns a dict with specific data for job creation of this class.
        It will be merged with the general self.get_job_data dict.

        :returns: job specific data
        :rtype: dict
        """
        return {}

    def get_job_data(self):
        """
        Returns the data to put into AWS. It is specific for the type of Job implementation.

        :returns: the dict with the job data in boto style
        :rtype: dict
        """
        data = {
            'Format': self.request_format,
            'SNSTopic': self.sns_topic_arn,
            'Type': self.type,
        }

        if self.description is not None and len(self.description) > 0:
            data['Description'] = self.description

        return dict(data.items() + self.__get_specific_job_data().items())


class InventoryRetrievalJob(Job):
    """
    Job for getting the inventory of a vault.
    """

    @property
    def type(self):
        """
        The job type,
        """
        return 'inventory-retrieval'

    class Meta:
        verbose_name = ugettext_lazy('Inventory retrieval job')
        verbose_name_plural = ugettext_lazy('Inventory retrieval jobs')


class ArchiveRetrievalJob(Job):
    """
    Job for retrieving the archive of a vault.
    """

    @property
    def type(self):
        """
        The job type,
        """
        return 'archive-retrieval'

    archive_id = models.CharField(
        max_length=255,
        verbose_name=_('Archive ID'),
    )

    class Meta:
        verbose_name = ugettext_lazy('Archive retrieval job')
        verbose_name_plural = ugettext_lazy('Archive retrieval jobs')

    def __get_specific_job_data(self):
        """
        Returns a dict with specific data for job creation of this class.
        It will be merged with the general self.get_job_data dict.

        :returns: job specific data
        :rtype: dict
        """
        return {
            'ArchiveID': self.archive_id,
        }
