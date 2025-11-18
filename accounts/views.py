"""
Account views for authentication and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserProfileForm
from .models import User, UserFollow


def index(request):
    """Landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/index.html')


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


@login_required
def profile_view(request):
    """User profile page."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def toggle_theme(request):
    """Toggle user theme."""
    user = request.user
    user.theme = 'light' if user.theme == 'dark' else 'dark'
    user.save()
    return redirect(request.META.get('HTTP_REFERER', '/dashboard/'))


@login_required
def follow_user(request, user_id):
    """Follow a user."""
    try:
        target_user = User.objects.get(id=user_id)
        if target_user != request.user:
            UserFollow.objects.get_or_create(
                follower=request.user,
                following=target_user
            )
            messages.success(request, f'Now following {target_user.username}!')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect(request.META.get('HTTP_REFERER', '/dashboard/'))


@login_required
def unfollow_user(request, user_id):
    """Unfollow a user."""
    try:
        target_user = User.objects.get(id=user_id)
        UserFollow.objects.filter(
            follower=request.user,
            following=target_user
        ).delete()
        messages.info(request, f'Unfollowed {target_user.username}.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect(request.META.get('HTTP_REFERER', '/dashboard/'))


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    """Password reset request view."""
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetForm
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        messages.info(self.request, 'If an account exists with that email, password reset instructions have been sent.')
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset done view."""
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirm view."""
    template_name = 'accounts/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully!')
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view."""
    template_name = 'accounts/password_reset_complete.html'

