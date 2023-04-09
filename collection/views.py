from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from collection.models import Collection, CollectionBeatmap


@login_required
def home(request):
    # Minus by 1 because default collection is not counted
    collection_count = Collection.objects.filter(owner=request.user).count() - 1
    beatmap_count = CollectionBeatmap.objects.filter(collection__owner=request.user).count()
    return render(request, 'collection/home.html', {
        'collection_count': collection_count,
        'beatmap_count': beatmap_count
    })


@login_required
def collection_list(request):
    collections = Collection.objects.filter(owner=request.user).order_by('name')
    return render(request, 'collection/list.html', {
        'collections': collections
    })


@login_required
def collection_detail(request, collection_id):
    # TODO: Pagination
    collection = Collection.objects.get(id=collection_id)
    beatmaps = CollectionBeatmap.objects.filter(collection=collection).order_by('beatmap__beatmapset__artist', 'beatmap__beatmapset__title')
    # Group beatmapset by beatmapset_id
    beatmapsets = {}
    for collection_beatmap in beatmaps:
        beatmapset = collection_beatmap.beatmap.beatmapset
        if beatmapset not in beatmapsets:
            beatmapsets[beatmapset] = []
        beatmapsets[beatmapset].append(collection_beatmap.beatmap)
    return render(request, 'collection/detail.html', {
        'collection': collection,
        'beatmapsets': beatmapsets
    })
