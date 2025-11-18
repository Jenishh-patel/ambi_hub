from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserFollow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'current_level', 'total_xp', 'current_streak', 'theme']
    list_filter = ['theme', 'privacy_mode', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Gamification', {'fields': ('total_xp', 'current_level', 'current_streak', 'longest_streak', 'last_activity_date')}),
        ('Profile', {'fields': ('bio', 'avatar', 'theme', 'privacy_mode')}),
    )


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']

