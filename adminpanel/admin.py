from django.contrib import admin
from .models import GlobalChallenge, PlatformAnalytics


@admin.register(GlobalChallenge)
class GlobalChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'target_xp', 'start_date', 'end_date']
    list_filter = ['status', 'created_at']


@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_users', 'active_users', 'total_tasks_completed']
    list_filter = ['date']

