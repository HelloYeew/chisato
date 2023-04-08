from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from collection.models import Collection, CollectionBeatmap


@login_required
def home(request):
    collection_count = Collection.objects.filter(owner=request.user).count()
    beatmap_count = CollectionBeatmap.objects.filter(collection__owner=request.user).count()
    return render(request, 'collection/home.html', {
        'collection_count': collection_count,
        'beatmap_count': beatmap_count
    })
