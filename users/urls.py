from django.contrib.auth import views as auth_views
from django.urls import path

from users import views

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('logout/', views.LogoutAndRedirect.as_view(), name='logout'),
]
