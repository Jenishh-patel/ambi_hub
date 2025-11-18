from django.contrib import admin
from .models import Category, Task, DailySummary


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user', 'xp_multiplier']
    list_filter = ['category_type']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'awarded_xp', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'user__username']


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'tasks_completed', 'xp_earned']
    list_filter = ['date']

