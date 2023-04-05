from django.contrib import admin

from collection.models import Beatmap, BeatmapSet

admin.site.register(BeatmapSet)
admin.site.register(Beatmap)
