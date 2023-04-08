import requests
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from collection.models import Collection
from users.models import Settings, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Settings.objects.create(user=instance)
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_default_collection(sender, instance, created, **kwargs):
    if created:
        Collection.objects.create(
            name='All beatmaps',
            description='Default collection for all beatmaps',
            owner=instance,
            default_collection=True
        )


@receiver(user_logged_in)
def update_from_oauth(sender, user, request, **kwargs):
    profile = Profile.objects.get(user=request.user)
    if SocialAccount.objects.filter(user=request.user).exists() and not profile.oauth_first_migrate:
        data = SocialAccount.objects.get(user=request.user).extra_data
        if data["avatar_url"] is not None:
            avatar_pic = requests.get(data["avatar_url"])
            avatar_temp = NamedTemporaryFile(delete=True)
            avatar_temp.write(avatar_pic.content)
            avatar_temp.flush()
            profile.profile_picture.save(data["avatar_url"].split('?')[-1], File(avatar_temp), save=True)
            profile.profile_picture_url = data["avatar_url"]
        if data["cover_url"] is not None:
            cover_pic = requests.get(data["cover_url"])
            cover_temp = NamedTemporaryFile(delete=True)
            cover_temp.write(cover_pic.content)
            cover_temp.flush()
            profile.cover_picture.save(data["cover_url"].split('?')[-1], File(cover_temp), save=True)
            profile.cover_picture_url = data["cover_url"]
        profile.osu_username = data["username"]
        profile.oauth_first_migrate = True
        profile.save()
    else:
        profile.oauth_first_migrate = True
        profile.save()
