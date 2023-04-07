from django.contrib.auth.models import User
from django.db import models


class OsuDatabaseBackupFile(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='osu')
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.owner}'

    class Meta:
        db_table = 'backup_osu'
        verbose_name = 'Osu Database Backup File'
        verbose_name_plural = 'Osu Database Backup Files'


class CollectionDatabaseBackupFile(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='collection')
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.owner}'

    class Meta:
        db_table = 'backup_collection'
        verbose_name = 'Collection Database Backup File'
        verbose_name_plural = 'Collection Database Backup Files'
