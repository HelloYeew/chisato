from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views

from collection.models import Collection
from users.forms import UserSettingsForm
from users.models import Profile


class LogoutAndRedirect(auth_views.LogoutView):
    """Logout and redirect to the homepage."""

    def get_next_page(self):
        messages.success(self.request, 'You have been logged out.')
        return '/login'


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! Now you can login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


@login_required
def settings(request):
    if request.method == 'POST':
        settings_form = UserSettingsForm(request.POST, instance=request.user.settings)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Settings saved successfully.')
            return redirect('settings')
    else:
        settings_form = UserSettingsForm(instance=request.user.settings)
    try:
        if SocialAccount.objects.filter(user=request.user).exists():
            osu_username = SocialAccount.objects.get(user=request.user).extra_data["username"]
        else:
            osu_username = None
    except KeyError:
        osu_username = None
    return render(request, 'users/settings.html', {
        'settings_form': settings_form,
        'osu_username': osu_username,
        'profile': Profile.objects.get(user=request.user),
        'social_account': SocialAccount.objects.filter(user=request.user).first()
    })


def profile(request, user_id):
    return render(request, 'users/profile.html', {
        'profile': Profile.objects.get(user_id=user_id),
        'collections': Collection.objects.filter(owner_id=user_id, private=False),
        'navbar_transparent': True
    })
