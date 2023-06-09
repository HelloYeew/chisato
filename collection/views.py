from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from collection.forms import CollectionForm
from collection.models import Collection, CollectionBeatmap, CollectionBeatmapSet

BEATMAPSET_PER_PAGE = 30


@login_required
def home(request):
    # Minus by 1 because default collection is not counted
    collection_count = Collection.objects.filter(owner=request.user).count() - 1
    default_collection = Collection.objects.filter(owner=request.user, default_collection=True).first()
    beatmap_count = CollectionBeatmap.objects.filter(collection=default_collection).count()
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


def collection_detail(request, collection_id):
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1
    collection = Collection.objects.get(id=collection_id)
    if collection.private and collection.owner != request.user:
        return render(request, '404.html', status=404)
    # Get only beatmapsets using in this page
    beatmapset = CollectionBeatmapSet.objects.filter(collection=collection).order_by('beatmapset__artist', 'beatmapset__title')[(page_number - 1) * BEATMAPSET_PER_PAGE:page_number * BEATMAPSET_PER_PAGE]
    beatmapsets = {}
    for collection_beatmapset in beatmapset:
        all_beatmap = CollectionBeatmap.objects.filter(collection=collection, beatmap__beatmapset=collection_beatmapset.beatmapset)
        beatmap_only = []
        for beatmap in all_beatmap:
            beatmap_only.append(beatmap.beatmap)
        beatmapsets[collection_beatmapset.beatmapset] = beatmap_only
    print(beatmapsets)
    total_beatmapset = CollectionBeatmapSet.objects.filter(collection=collection).count()
    total_page = total_beatmapset // BEATMAPSET_PER_PAGE + 1
    if total_beatmapset % BEATMAPSET_PER_PAGE == 0:
        total_page -= 1
    if page_number > total_page != 0:
        # add page querystring to the url
        return redirect(reverse('collections_detail', kwargs={'collection_id': collection_id}) + f'?page={total_page}')
    if page_number == 0:
        return redirect(reverse('collections_detail', kwargs={'collection_id': collection_id}))
    if page_number < 0:
        return redirect(reverse('collections_detail', kwargs={'collection_id': collection_id}))
    # If number of beatmapsets is less than 20, then just show all beatmapsets
    if total_beatmapset <= BEATMAPSET_PER_PAGE:
        showing_string = f"Showing all {total_beatmapset} beatmapsets"
        return render(request, 'collection/detail.html', {
            'collection': collection,
            'beatmapsets': beatmapsets,
            'page_number': 1,
            'total_page': 1,
            'page_list': range(1, 2),
            'showing_string': showing_string
        })
    showing_string = f"Showing beatmapsets {BEATMAPSET_PER_PAGE * int(page_number) - BEATMAPSET_PER_PAGE + 1} to {BEATMAPSET_PER_PAGE * int(page_number) if BEATMAPSET_PER_PAGE * int(page_number) <= total_beatmapset else total_beatmapset} of {total_beatmapset}"
    return render(request, 'collection/detail.html', {
        'collection': collection,
        'beatmapsets': beatmapsets,
        'page_number': page_number if page_number <= total_page else total_page,
        'total_page': total_page,
        'page_list': range(1, total_page + 1),
        'showing_string': showing_string
    })


def edit_collection(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    if collection.owner != request.user:
        return render(request, '404.html', status=404)
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            collection.name = form.cleaned_data['name']
            collection.private = form.cleaned_data['private']
            collection.description = form.cleaned_data['description']
            collection.save()
            messages.success(request, 'Collection updated successfully!')
            return redirect(reverse('collections_detail', kwargs={'collection_id': collection_id}))
    else:
        form = CollectionForm(instance=collection)
    return render(request, 'collection/edit.html', {
        'collection': collection,
        'form': form
    })
