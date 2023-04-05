from django.contrib.auth import views as auth_views
from django.urls import path

from users import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.LogoutAndRedirect.as_view(), name='logout'),
]
