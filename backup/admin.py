from django.contrib import admin

from backup.models import OsuDatabaseBackupFile, CollectionDatabaseBackupFile

admin.site.register(OsuDatabaseBackupFile)
admin.site.register(CollectionDatabaseBackupFile)
