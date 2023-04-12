from django.urls import path

from collection import views

urlpatterns = [
    path('', views.home, name='collections_home'),
    path('list', views.collection_list, name='collections_list'),
    path('detail/<int:collection_id>', views.collection_detail, name='collections_detail'),
    path('detail/<int:collection_id>/edit', views.edit_collection, name='collections_edit')
]
