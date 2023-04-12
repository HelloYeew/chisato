"""
Database models for all collection and osu! beatmap related models.
Structure of database models originally from
- [beattosetto](https://github.com/beattosetto/beattosetto/blob/main/beatmap_collections/models.py)
- [Freedom Dive mirror](https://github.com/HelloYeew/freedom-dive/blob/main/mirror/models.py)
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class BeatmapSet(models.Model):
    """
    Database table to store the beatmapset detail.
    For more information see https://github.com/ppy/osu-api/wiki
    """
    beatmapset_id = models.IntegerField(primary_key=True)
    artist = models.CharField(max_length=255)
    artist_unicode = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    title_unicode = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255)
    tags = models.CharField(max_length=1000)
    video = models.BooleanField(default=False)
    storyboard = models.BooleanField(default=False)
    bpm = models.FloatField(default=0)
    approved = models.IntegerField(default=0)
    approved_date = models.DateTimeField(default=None, null=True)
    submit_date = models.DateTimeField(default=None, null=True)
    last_update = models.DateTimeField(default=None, null=True)
    genre_id = models.IntegerField(default=0)
    language_id = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    play_count = models.IntegerField(default=0)

    card_picture_url = models.URLField(default=None, null=True)
    list_picture_url = models.URLField(default=None, null=True)
    cover_picture_url = models.URLField(default=None, null=True)
    full_size_picture_url = models.URLField(default=None, null=True)
    thumbnail_picture_url = models.URLField(default=None, null=True)

    def __str__(self):
        return self.artist + ' - ' + self.title

    class Meta:
        db_table = 'collection_beatmapset'
        verbose_name = 'Beatmap Set'
        verbose_name_plural = 'Beatmap Sets'


class Beatmap(models.Model):
    """
    Database table to store the beatmap detail.
    For more information see https://github.com/ppy/osu-api/wiki
    """
    beatmap_id = models.IntegerField(primary_key=True)
    beatmapset = models.ForeignKey(BeatmapSet, on_delete=models.CASCADE)
    creator = models.CharField(max_length=255)
    creator_id = models.IntegerField()
    checksum = models.CharField(max_length=32)
    version = models.CharField(max_length=255)
    total_length = models.IntegerField(default=0)
    hit_length = models.IntegerField(default=0)
    count_total = models.IntegerField(default=0)
    count_normal = models.IntegerField(default=0)
    count_slider = models.IntegerField(default=0)
    count_spinner = models.IntegerField(default=0)
    diff_drain = models.FloatField(default=0)
    diff_size = models.FloatField(default=0)
    diff_overall = models.FloatField(default=0)
    diff_approach = models.FloatField(default=0)
    play_mode = models.IntegerField(default=0)
    approved = models.IntegerField(default=0)
    last_update = models.DateTimeField(default=timezone.now, null=True)
    difficulty_rating = models.FloatField(default=0)
    play_count = models.IntegerField(default=0)
    pass_count = models.IntegerField(default=0)
    bpm = models.FloatField(default=0)

    def __str__(self):
        return self.beatmapset.artist + ' - ' + self.beatmapset.title + ' [' + self.version + ']'

    class Meta:
        db_table = 'collection_beatmap'
        verbose_name = 'Beatmap'
        verbose_name_plural = 'Beatmaps'


class Collection(models.Model):
    """
    Database table to store the collection detail/
    """
    name = models.CharField(max_length=255)
    # Original name from the collection database file
    file_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    default_collection = models.BooleanField(default=False)
    private = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.owner} (default: {self.default_collection})'

    class Meta:
        db_table = 'collection_collection'
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'


class CollectionBeatmap(models.Model):
    """
    Database table to store the beatmap in collection.
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    beatmap = models.ForeignKey(Beatmap, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.collection.name + ' - ' + self.beatmap.beatmapset.artist + ' - ' + self.beatmap.beatmapset.title + ' [' + self.beatmap.version + ']'

    class Meta:
        db_table = 'collection_collectionbeatmap'
        verbose_name = 'Collection Beatmap'
        verbose_name_plural = 'Collection Beatmaps'
        unique_together = ('collection', 'beatmap')
