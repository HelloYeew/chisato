# Generated by Django 4.2 on 2023-04-07 04:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OsuDatabaseBackupFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file_name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='osu')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Osu Database Backup File',
                'verbose_name_plural': 'Osu Database Backup Files',
                'db_table': ('backup_osu'),
            },
        ),
        migrations.CreateModel(
            name='CollectionDatabaseBackupFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file_name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='collection')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Collection Database Backup File',
                'verbose_name_plural': 'Collection Database Backup Files',
                'db_table': ('backup_collection'),
            },
        ),
    ]
