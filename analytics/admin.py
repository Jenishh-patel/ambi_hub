from django.contrib import admin
from .models import UserReport


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'start_date', 'end_date', 'generated_at']
    list_filter = ['report_type', 'generated_at']

