from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from PIL import Image


THEME_SETTINGS = (
    ('', 'Default'),
    ('green', 'Green'),
    ('dark', 'Dark Default'),
)


class Profile(models.Model):
    """Profile model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='default_pfp.png', upload_to='profile_pictures',
                        validators=[FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])
    profile_picture_url = models.URLField(max_length=200, blank=True)
    cover_picture = models.ImageField(default='default_cover.png', upload_to='cover_pictures',
                        validators=[FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])
    cover_picture_url = models.URLField(max_length=200, blank=True)
    osu_username = models.CharField(max_length=32, blank=True)
    oauth_first_migrate = models.BooleanField(default=False)

    def __str__(self):
        """Return username."""
        return self.user.username + ' profile'

    def save(self, *args, **kwargs):
        """Resize profile and cover image"""
        super().save(*args, **kwargs)
        # Resize image using PIL
        if self.profile_picture and self.profile_picture.name != 'default_pfp.png':
            profile_image = Image.open(self.profile_picture.path)
            if profile_image.height > 256 or profile_image.width > 256:
                output_size = (256, 256)
                profile_image.thumbnail(output_size)
                profile_image.save(self.profile_picture.path)
        if self.cover_picture and self.cover_picture.name != 'default_cover.png':
            cover_image = Image.open(self.cover_picture.path)
            if cover_image.height > 1920 or cover_image.width > 1080:
                output_size = (1920, 1080)
                cover_image.thumbnail(output_size)
                cover_image.save(self.cover_picture.path)


class Settings(models.Model):
    """Settings model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, choices=THEME_SETTINGS, default='', blank=True)

    class Meta:
        """Meta class."""
        db_table = 'users_settings'
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'

    def __str__(self):
        """Return name."""
        return self.user.username + ' settings'
