from django.contrib import admin
from django.utils.translation import ugettext_lazy

from glacier_backup.models import (
    Archive,
    ArchiveRetrievalJob,
    InventoryRetrievalJob,
    Vault,
)


class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'vault', 'status', )
    date_hierarchy = 'created'
    ordering = ('created', 'vault', 'status', )
    search_fields = ('title', 'vault', 'created',)


class VaultAdmin(admin.ModelAdmin):
    actions = ['inventory', ]

    def inventory(self, request, queryset):
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
    list_display = ('vault', 'status', 'date_completion', 'date_updated', 'date_creation', 'job_id', )
    date_hierarchy = 'date_creation'
    ordering = ('date_updated', )
    search_fields = ('job_id', )


class InventoryRetrievalJobAdmin(JobAdmin):
    pass


class ArchiveRetrievalJobAdmin(JobAdmin):
    pass

admin.site.register(Archive, ArchiveAdmin)
admin.site.register(Vault, VaultAdmin)
admin.site.register(InventoryRetrievalJob, InventoryRetrievalJobAdmin)
admin.site.register(ArchiveRetrievalJob, ArchiveRetrievalJobAdmin)