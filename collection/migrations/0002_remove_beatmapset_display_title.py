# Generated by Django 4.2 on 2023-04-05 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beatmapset',
            name='display_title',
        ),
    ]
