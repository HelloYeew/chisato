from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from collection.models import Collection
from users.models import Settings


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Settings.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_default_collection(sender, instance, created, **kwargs):
    if created:
        Collection.objects.create(
            name='All beatmaps',
            description='Default collection for all beatmaps',
            owner=instance,
            default_collection=True
        )
