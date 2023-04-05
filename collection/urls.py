from django.urls import path

from collection import views

urlpatterns = [
    path('', views.home, name='collections_home')
]
