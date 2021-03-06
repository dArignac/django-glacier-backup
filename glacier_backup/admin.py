"""Admin site definitions"""
from django.contrib import admin, messages
from django.utils.translation import ugettext as _, ugettext_lazy

from glacier_backup.models import (
    Archive,
    ArchiveRetrievalJob,
    InventoryRetrievalJob,
    Vault,
)


class ArchiveAdmin(admin.ModelAdmin):

    """Admin for Archive class"""

    list_display = ('title', 'created', 'vault', 'status', )
    date_hierarchy = 'created'
    ordering = ('created', 'vault', 'status', )
    search_fields = ('title', 'vault', 'created',)
    actions = ['download', ]

    def download(self, request, queryset):
        """
        Queues the archive for download.

        :param request: the sent request
        :param queryset: the queryset containing the selected archives
        :type request: django.core.handlers.wsgi.WSGIRequest
        :type queryset: django.db.models.query.QuerySet
        """
        for archive in queryset.all():
            archive.download()

        messages.add_message(request, messages.SUCCESS, _('Successfully created %(count)d archive retrieval jobs.') % {
            'count': queryset.count(),
        })

    download.short_description = ugettext_lazy('Download')


class VaultAdmin(admin.ModelAdmin):

    """Admin for Vault class"""

    actions = ['inventory', ]

    def inventory(self, request, queryset):  # pylint:disable=unused-argument
        """
        Inventories the selected vaults.

        :param request: the sent request
        :param queryset: the queryset containing the selected vaults
        :type request: django.core.handlers.wsgi.WSGIRequest
        :type queryset: django.db.models.query.QuerySet
        """
        for vault in queryset.all():
            vault.inventory()
    inventory.short_description = ugettext_lazy('Inventory vaults')


class JobAdmin(admin.ModelAdmin):

    """Admin for Job class"""

    list_display = ('vault', 'status', 'date_completion', 'date_updated', 'date_creation', 'job_id', )
    date_hierarchy = 'date_creation'
    ordering = ('date_updated', )
    search_fields = ('job_id', )


class InventoryRetrievalJobAdmin(JobAdmin):

    """Admin for InventoryRetrievalJob class"""

    pass


class ArchiveRetrievalJobAdmin(JobAdmin):

    """Admin for ArchiveRetrievalJob class"""

    pass

admin.site.register(Archive, ArchiveAdmin)
admin.site.register(Vault, VaultAdmin)
admin.site.register(InventoryRetrievalJob, InventoryRetrievalJobAdmin)
admin.site.register(ArchiveRetrievalJob, ArchiveRetrievalJobAdmin)