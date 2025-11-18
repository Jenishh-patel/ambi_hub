"""
Forms for account management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """User registration form."""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """User profile edit form."""
    class Meta:
        model = User
        fields = ['email', 'bio', 'avatar', 'privacy_mode']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

