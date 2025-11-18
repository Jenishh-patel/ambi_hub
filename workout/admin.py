from django.contrib import admin
from .models import Exercise, WorkoutSession, SetEntry, PersonalRecord


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'user', 'is_default', 'created_at']
    list_filter = ['category', 'is_default']
    search_fields = ['name']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_volume', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['user__username']


@admin.register(SetEntry)
class SetEntryAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise', 'reps', 'weight', 'volume', 'set_number']
    list_filter = ['exercise', 'session__date']


@admin.register(PersonalRecord)
class PersonalRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'max_weight', 'date_achieved']
    list_filter = ['exercise', 'date_achieved']

