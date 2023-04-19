from django.contrib import admin

from collection.models import Beatmap, BeatmapSet, Collection, CollectionBeatmap, CollectionBeatmapSet

admin.site.register(BeatmapSet)
admin.site.register(Beatmap)
admin.site.register(Collection)
admin.site.register(CollectionBeatmap)
admin.site.register(CollectionBeatmapSet)
