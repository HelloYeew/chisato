from django.urls import path

from backup import views

urlpatterns = [
    path('home', views.home, name='backup_home'),
    path('upload', views.upload, name='backup_upload')
]
